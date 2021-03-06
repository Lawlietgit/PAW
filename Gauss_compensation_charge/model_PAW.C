//==========================================================================
//cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
//==========================================================================
//
//  This program computes the compensation charg energy for a frozen Gaussian
//	core density
//
//==========================================================================
//cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
//==========================================================================
// Standard include files

#include "standard_include.h"
#include "ckcomplex.h"
#include "fgrid.h"
#include "GaussianPAW.h"
#include "grid.h"
#include "gen_Gauss_quad_driver_entry.h"

//==========================================================================
//cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
//==========================================================================
//  Main Program : Controller to manage compensation charge energy
//==========================================================================
int main (int argc, char *argv[]){
  //==========================================================================
  // Local variables
  ATOM_MAPS atom_maps;
  ATOM_POS  atom_pos;
  ATOM_POS  atom_pos_dummy;
  CELL      cell;

  int natm_typ;       	// number of atom types
  int natm;				// number of atoms
  int *index_atm_typ;	// index of atom type of each atom
  int *natm_atm_typ;	// the number of atoms of each type
  int **list_atm_by_typ;// list of atoms sorted by atom type
  NAME *atm_typ;	    // names of the atom types

  int iperd = 3;		// periodicity
  double alpb;			// Ewald alpha
  double gcut;		    // Ewald reciprocal space cutoff 

  double *x,*y,*z,*q,*qt,*alp,*beta;    // atom positions and core Gaussian parameters
  double hmat[10];				  // the simulation box
  double hmati[10];				  // inverse simulation box
  double volume;				  // simulation box volume

  int rorder;
  int thetaorder; 
  int phiorder;    // grid sizes
  int lmax;									// maximum angular momentum
  double delta = 1e-6;
	double beta_unitless;       // unitless beta for screening, beta[J] = alpha[J]*beta_unitless

  ESTRUCT energy;		// compensation charge energy terms stored nicely
  ESTRUCT *energy_plus  = new ESTRUCT [3]; 		
  ESTRUCT *energy_minus = new ESTRUCT [3]; 		
		
  strcpy(energy.ENN.name           		, "E_NN_0D             ");
  strcpy(energy.EeN.name           		, "E_eN_0D             ");
  strcpy(energy.EeNself.name       		, "E_eNself_0D         ");
  strcpy(energy.EHar.name          		, "E_Har_0D            ");
  strcpy(energy.EHarself.name      		, "E_Har_self_0D       ");
  strcpy(energy.ENNshort.name      		, "E_NNshort_3D        ");
  strcpy(energy.EeNshort.name      		, "E_eN_short_3D       ");
  strcpy(energy.EeNshortself.name  		, "E_eN_short_self_3D  ");
  strcpy(energy.EHarshort.name     		, "E_Har_short_3D      ");
  strcpy(energy.EHarshortself.name 		, "E_Har_short_self_3D ");
  strcpy(energy.Elong.name         		, "E_long_3D           ");
  strcpy(energy.ENNselflong.name   		, "E_NNselflong_3D     ");
  strcpy(energy.Etot0D.name        		, "E_tot_0D            ");
  strcpy(energy.Etot3D.name        		, "E_tot_3D            ");
  strcpy(energy.EHarselfscr.name		, "E_Har_self_0D_scr   ");

  long seed;		// random seeds
  double dseed;		// random seeds

  char fnameIn[MAXLINE];

  FILE *fp;

  //==========================================================================
  // Tell everyone what you are doing

  PRINTF("\n");
  PRINT_LINE_STAR
    PRINTF("Test a model PAW energy\n");
  PRINT_LINE_DASH

    //=========================================================================
    //             Check for input file                                 

    if(argc < 7) {
      PRINTF("@@@@@@@@@@@@@@@@@@@@_error_@@@@@@@@@@@@@@@@@@@@\n");
      PRINTF("No input file specified!\n");
      PRINTF("Run it like: ./model_PAW.x PAW.in rorder thetaorder phiorder lmax beta_unitless\n");
      PRINTF("@@@@@@@@@@@@@@@@@@@@_error_@@@@@@@@@@@@@@@@@@@@\n");
      FFLUSH(stdout);
      EXIT(1);
    }/*endif*/

  //==========================================================================
  // Read the user specified input file: atoms, Ewald parameters, core density parameters and box
  // store the information

  rorder 	 = atoi(argv[2]);
  thetaorder = atoi(argv[3]);
  phiorder   = atoi(argv[4]);
  lmax 	 	 = atoi(argv[5]);
  beta_unitless 	 	 = atof(argv[6]);
  strcpy(fnameIn, argv[1]);
  PRINTF("\nReading input parameters and atom positions from %s\n\n",fnameIn);
  fp = fopen(fnameIn,"r");
  	fscanf(fp,"%d %d", &natm, &natm_typ); readtoendofline(fp);
	atm_typ = new NAME [natm_typ];
  	natm_atm_typ = new int [natm_typ];
	int natm_atm_typ_max = 0;
	for (int i=0; i<natm_typ; i++) { 
		int j;
		fscanf(fp,"%d %d %s", &j, &natm_atm_typ[i], atm_typ[i]); readtoendofline(fp);
		if (j != i) {
     		PRINTF("@@@@@@@@@@@@@@@@@@@@_error_@@@@@@@@@@@@@@@@@@@@\n");
      		PRINTF("atom type out of order!\n");
      		PRINTF("@@@@@@@@@@@@@@@@@@@@_error_@@@@@@@@@@@@@@@@@@@@\n");
      		FFLUSH(stdout);
      		EXIT(1);
		} 
		natm_atm_typ_max = MAX(natm_atm_typ_max,natm_atm_typ[i]);
		PRINT_LINE_DASH;
  		PRINTF("Number of atom %s: %d\n",atm_typ[i], natm_atm_typ[i]);
	} // end for i
	PRINT_LINE_STAR;
	PRINTF("\n");
  	fscanf(fp,"%lf %lf",&alpb, &gcut); readtoendofline(fp);

  	x = new double [natm]; y = new double [natm]; z = new double [natm];
  	q = new double [natm]; qt = new double [natm];
  	alp = new double [natm]; beta = new double [natm];

  	double *vx   = new double [natm]; double *vy   = new double [natm]; double *vz   = new double [natm];
  	double *fx0  = new double [natm]; double *fy0  = new double [natm]; double *fz0  = new double [natm];
  	double *fx   = new double [natm]; double *fy   = new double [natm]; double *fz   = new double [natm];
  	double *fx0g = new double [natm]; double *fy0g = new double [natm]; double *fz0g = new double [natm];
  	double *fxg  = new double [natm]; double *fyg  = new double [natm]; double *fzg  = new double [natm];

	index_atm_typ = new int [natm];
	list_atm_by_typ = new int *[natm_typ];
	for (int i=0; i<natm_typ; i++) { list_atm_by_typ[i] = new int [natm_atm_typ_max]; }
  	for (int i=0; i<natm; i++) {
  		fscanf(fp,"%lf %lf %lf %lf %lf %lf %d",&x[i],&y[i],&z[i], &q[i], &qt[i], &alp[i], &index_atm_typ[i]); readtoendofline(fp);
		beta[i] = alp[i]*beta_unitless;
  	} //end for i
  	fscanf(fp, "%lf %lf %lf", &hmat[1], &hmat[4], &hmat[7]); readtoendofline(fp);
  	fscanf(fp, "%lf %lf %lf", &hmat[2], &hmat[5], &hmat[8]); readtoendofline(fp);
  	fscanf(fp, "%lf %lf %lf", &hmat[3], &hmat[6], &hmat[9]); readtoendofline(fp);
  fclose(fp);

  for (int i=0; i<natm; i++) {
	vx[i]   = 0; vy[i]   = 0; vz[i]   = 0;
	fx0[i]  = 0; fy0[i]  = 0; fz0[i]  = 0;
	fx[i]   = 0; fy[i]   = 0; fz[i]   = 0;
	fx0g[i] = 0; fy0g[i] = 0; fz0g[i] = 0;
	fxg[i]  = 0; fyg[i]  = 0; fzg[i]  = 0;
  } // end for

#ifdef _FORCECHECK_
  //========================================================================
  // make a copy of the atoms: give the dummy structure its own memory!!!!!!

  double *xd = new double [natm]; double *yd = new double [natm]; double *zd = new double [natm];
  double *qd = new double [natm]; double *qtd = new double [natm];
  double *alpd = new double [natm];

  double *vxd   = new double [natm]; double *vyd   = new double [natm]; double *vzd   = new double [natm];
  double *fx0d  = new double [natm]; double *fy0d  = new double [natm]; double *fz0d  = new double [natm];
  double *fxd   = new double [natm]; double *fyd   = new double [natm]; double *fzd   = new double [natm];
  double *fx0gd = new double [natm]; double *fy0gd = new double [natm]; double *fz0gd = new double [natm];
  double *fxgd  = new double [natm]; double *fygd  = new double [natm]; double *fzgd  = new double [natm];

  for (int i=0; i<natm; i++) {
	vxd[i]   = 0; vyd[i]   = 0; vzd[i]   = 0;
	fx0d[i]  = 0; fy0d[i]  = 0; fz0d[i]  = 0;
	fxd[i]   = 0; fyd[i]   = 0; fzd[i]   = 0;
	fx0gd[i] = 0; fy0gd[i] = 0; fz0gd[i] = 0;
	fxgd[i]  = 0; fygd[i]  = 0; fzgd[i]  = 0;
	
	xd[i]   = x[i]; yd[i]   = y[i]; zd[i]   = z[i];
	qd[i]   = q[i]; qtd[i]  = qt[i];
    alpd[i] = alp[i];
  } // end for
#endif // _FORCECHECK_

  //========================================================================
  // store the atom information: this is safe because the dummy has its own memory
 
  atom_pos.natm	= natm;
  atom_pos.x 	= x;    atom_pos.y 	  = y;    atom_pos.z    = z;
  atom_pos.q 	= q;
  atom_pos.qt 	= qt;
  atom_pos.alp 	= alp; atom_pos.beta  = beta;

  atom_pos.vx	= vx;   atom_pos.vy   = vy;   atom_pos.vz   = vz;
  atom_pos.fx0	= fx0;  atom_pos.fy0  = fy0;  atom_pos.fz0  = fz0;
  atom_pos.fx	= fx;   atom_pos.fy   = fy;   atom_pos.fz   = fz;
  atom_pos.fx0g	= fx0g; atom_pos.fy0g = fy0g; atom_pos.fz0g = fz0g;
  atom_pos.fxg	= fxg;  atom_pos.fyg  = fyg;  atom_pos.fzg  = fzg;

#ifdef _FORCECHECK_
  atom_pos_dummy.natm	= natm;
  atom_pos_dummy.x 		= xd;    atom_pos_dummy.y 	  = yd;    atom_pos_dummy.z    = zd;
  atom_pos_dummy.q 		= qd;
  atom_pos_dummy.qt 	= qtd;
  atom_pos_dummy.alp 	= alpd;

  atom_pos_dummy.vx		= vxd;   atom_pos_dummy.vy   = vyd;   atom_pos_dummy.vz   = vzd;
  atom_pos_dummy.fx0	= fx0d;  atom_pos_dummy.fy0  = fy0d;  atom_pos_dummy.fz0  = fz0d;
  atom_pos_dummy.fx		= fxd;   atom_pos_dummy.fy   = fyd;   atom_pos_dummy.fz   = fzd;
  atom_pos_dummy.fx0g	= fx0gd; atom_pos_dummy.fy0g = fy0gd; atom_pos_dummy.fz0g = fz0gd;
  atom_pos_dummy.fxg	= fxgd;  atom_pos_dummy.fyg  = fygd;  atom_pos_dummy.fzg  = fzgd;
#endif // _FORCECHECK_

  //========================================================================
  // compute and store the atom maps

  int *natm_typ_now = new int[natm_typ];
  for (int i=0; i<natm_typ; i++) { natm_typ_now[i] = 0; }
  for (int i=0; i<natm; i++) { 
	int ityp = index_atm_typ[i];
	list_atm_by_typ[ityp][natm_typ_now[ityp]] = i;
	natm_typ_now[ityp]++; 
  } // end for
  delete [] natm_typ_now;
  atom_maps.natm_typ 			= natm_typ;
  atom_maps.natm				= natm;		 
  atom_maps.index_atm_typ   	= index_atm_typ;	
  atom_maps.natm_atm_typ    	= natm_atm_typ;
  atom_maps.list_atm_by_typ 	= list_atm_by_typ;
  atom_maps.atm_typ				= atm_typ;	    
  atom_maps.natm_atm_typ_max 	= natm_atm_typ_max;

  gethinv(hmat, hmati, &volume, iperd);
  gcut *= alpb;

  //========================================================================
  // store the simulation cell information 
  cell.iperd 					= iperd;		
  cell.alpb						= alpb;			
  cell.gcut						= gcut;		   
  for (int i=1; i<10; i++) {
  	cell.hmat[i]	    		= hmat[i];				 
  }				 
  gethinv(hmat, hmati, &volume, iperd);
  for (int i=1; i<10; i++) {
  	cell.hmati[i]   	 		= hmati[i];
  }				 
  cell.volume    			    = volume;

  //========================================================================
  // compute the grids 
  int nf = rorder*thetaorder*phiorder;
  FGRID *fgrid = new FGRID [natm_typ];      // fgrid structure

  //---------------------------------------------------------------------
  // get the master Gauss-Legendre, Gauss_Hermite_half, and phi grids

  double * xr_master = new double [rorder]; double * wr_master = new double [rorder];
  double * xphi_master = new double [phiorder]; double * wphi_master = new double [phiorder];
  double * xtheta_master = new double [thetaorder]; double * wtheta_master = new double [thetaorder];
 
  int kind = 0; 
//double aaa = -1; double bbb = 1;
  int type = 2; int iopt = 0;
// control_quad_rule(kind, thetaorder, aaa, bbb, wtheta_master, xtheta_master); // Legendre 
  int ierr_zero1; int ierr_ortho1;
  gen_Gauss_quad_driver(kind, thetaorder, iopt, xtheta_master, wtheta_master, &ierr_zero1, &ierr_ortho1);

  int ierr_zero; int ierr_ortho;
  gen_Gauss_quad_driver(type, rorder, iopt, xr_master, wr_master, &ierr_zero, &ierr_ortho);

  genphigrid(phiorder,wphi_master,xphi_master); // Fourier (equal space)

 
  //---------------------------------------------------------------------
  // use the master quadratures to create the full fgrid

  for (int i=0; i<natm_typ; i++) {
  	fgrid[i].nf = nf;
  	fgrid[i].nr = rorder;
  	fgrid[i].ntheta = thetaorder;
  	fgrid[i].nphi = phiorder;
  	fgrid[i].wf = new double [nf];
  	fgrid[i].xf = new double [nf];
  	fgrid[i].yf = new double [nf];
  	fgrid[i].zf = new double [nf];
  	fgrid[i].rf = new double [nf];
  	fgrid[i].xcostheta = new double [thetaorder];
  	fgrid[i].xphi = new double [phiorder];
	fgrid[i].Ylmf = new complex [nf];
  	fgrid[i].xr = new double [rorder];
  	fgrid[i].wr = new double [rorder];
	int J = list_atm_by_typ[i][0];
	double alp_tmp = alp[J];
	double beta_tmp = beta[J];
	fgrid[i].alp = alp_tmp;
	fgrid[i].beta = beta_tmp;

    double *wf = fgrid[i].wf;
    double *xf = fgrid[i].xf;
    double *yf = fgrid[i].yf;
    double *zf = fgrid[i].zf;
    double *rf = fgrid[i].rf;
    double *xr = fgrid[i].xr;
    double *wr = fgrid[i].wr;
	double *xcostheta = fgrid[i].xcostheta;
	double *xphi = fgrid[i].xphi;
	
	double result = 0.0;
	double result2 = 0.0;

	for (int ir=0; ir<rorder; ir++) {
		xr[ir] = xr_master[ir]/alp_tmp;
		wr[ir] = wr_master[ir]/alp_tmp;
		result += wr[ir];
		result2 += wr[ir]*xr[ir]*xr[ir];
	} // end for ir
//	PRINTF("test %g %g %g %g %g\n", result, result2, sqrt(M_PI_QI)*0.5, sqrt(M_PI_QI)*0.25, alp_tmp);
	
	double result3 = 0.0;
	double result4 = 0.0;
	double pre3 = 8.0/M_PI_QI*pow(alp_tmp,6);
	double beta2 = beta_tmp*beta_tmp;
	for (int ir=0; ir<rorder; ir++) {
		for (int jr=0; jr<rorder; jr++) {
			double rgt = MAX(xr[ir],xr[jr]);
			double rlt = MIN(xr[ir],xr[jr]);
			double rd = rgt - rlt;
			double rs = rgt + rlt;
			result3 += wr[ir]*wr[jr]*xr[ir]*xr[ir]*xr[jr]*xr[jr]/rgt;
			double complicated;
			double part1 = (exp(-beta2*rs*rs) - exp(-beta2*rd*rd))/(2.0*beta_tmp*sqrt(M_PI_QI)*rgt*rlt); 
			double part2 = (rd*erfc(beta_tmp*rd) - rs*erfc(beta_tmp*rs))/(2.0*rgt*rlt);
			double part3 = 1.0/rgt;
			complicated = part1 + part2 + part3; 
			result4 += wr[ir]*wr[jr]*xr[ir]*xr[ir]*xr[jr]*xr[jr]*complicated;
		} // end for jr
	} // end for ir
	result3 *= pre3;
	result4 *= pre3;
	PRINTF("test3: %g %g\n", result3, alp_tmp/sqrt(2.0*M_PI_QI));
	
	double gamma2_inv = 0.5/(alp_tmp*alp_tmp) + 0.25/(beta_tmp*beta_tmp);
	double gamma = 1.0/sqrt(gamma2_inv);
	PRINTF("test4: %.10g %.10g beta_tmp = %g\n", result4, 0.5*gamma/sqrt(M_PI_QI), beta_tmp);

	for (int itheta=0; itheta<thetaorder; itheta++) { xcostheta[itheta] = xtheta_master[itheta];}
	for (int iphi=0; iphi<phiorder; iphi++) { xphi[iphi] = xphi_master[iphi];}

    int f = 0;
    for (int ir=0; ir<rorder; ir++) {
        for (int itheta=0; itheta<thetaorder; itheta++) {
            for (int iphi=0; iphi<phiorder; iphi++) {
                double xsintheta = sqrt(1.0-(xtheta_master[itheta])*(xtheta_master[itheta]));
                wf[f] = wr[ir]*xr[ir]*xr[ir]*wtheta_master[itheta]*wphi_master[iphi];
                xf[f] = xr[ir]*xsintheta*cos(xphi_master[iphi]);
                yf[f] = xr[ir]*xsintheta*sin(xphi_master[iphi]);
                zf[f] = xr[ir]*xtheta_master[itheta];
                rf[f] = xr[ir];
//				double tmp = xf[f]*xf[f] + yf[f]*yf[f] + zf[f]*zf[f] - rf[f]*rf[f];
//				PRINTF("\ntest square relation: %g\n", tmp);
                f++;
            } // end for iphi
        } // end for itheta
    } // end for ir
  } // end for

  //========================================================================
  // Compute the real space energy analytically
  
  computePAWreal(&atom_maps, &atom_pos, &cell, &energy);

  //========================================================================
  // Compute the long range energy analytically

  computePAWlong(&atom_maps, &atom_pos, &cell, &energy, fgrid);

  //========================================================================
  // Compute the real space energy on grid

  computePAWGrid(lmax, &atom_maps, &atom_pos, &cell, &energy, fgrid);

  energy.Etot0D.E     = energy.ENN.E + energy.EeN.E + energy.EHar.E;
  energy.Etot0D.EGrid = energy.ENN.EGrid + energy.EeN.EGrid + energy.EHar.EGrid;
// energy.Etot3D.E     = energy.ENNshort.E + energy.EeNshort.E + energy.EHarshort.E + energy.Elong.E - energy.ENNselflong.E;
// energy.Etot3D.EGrid = energy.ENNshort.EGrid + energy.EeNshort.EGrid + energy.EHarshort.EGrid + energy.Elong.EGrid - energy.ENNselflong.EGrid;
  energy.Etot3D.E     = energy.ENNshort.E + energy.EeNshort.E + energy.Elong.E - energy.ENNselflong.E;
  energy.Etot3D.EGrid = energy.ENNshort.EGrid + energy.EeNshort.EGrid + energy.Elong.EGrid - energy.ENNselflong.EGrid;

  //========================================================================
  // Print out the energy

  PRINT_LINE_STAR;
  PRINTF(" Printing out results: analytical, f-grid, and error\n");
  PRINT_LINE_DASH;
  PRINTF("Energy                |    Analytic   |   Grid       |  Diff       |  %%Diff\n");
  PRINT_LINE_DASH;
  //----------------------------------------- 
  //Printing the 0D energies
  energy.ENN.pres();
  energy.EeN.pres();
  energy.EeNself.pres();
  energy.EHar.pres();
  energy.EHarself.pres();
  //----------------------------------------- 
  //Printing the 3D short range energies
  PRINT_LINE_DASH;    
  energy.ENNshort.pres();
  energy.EeNshort.pres();
  energy.EeNshortself.pres();
  energy.EHarshort.pres();
  energy.EHarshortself.pres();
  //----------------------------------------- 
  //Printing the 3D long range energies
  PRINT_LINE_DASH;
  energy.ENNselflong.pres();
  energy.Elong.pres();
  //----------------------------------------- 
  //Printing the 0D and 3D total energies
  PRINT_LINE_DASH;
  energy.Etot0D.pres();
  energy.Etot3D.pres();
  energy.EHarselfscr.pres();
  PRINT_LINE_DASH;
  PRINTF(" Completed output\n");
  PRINT_LINE_STAR;
  PRINTF("\n");
  //==========================================================================
// } //end for loop over r grid sizes
  //==========================================================================
  //==========================================================================
  // Tell everyone you are done

  PRINT_LINE_DASH
  PRINTF("Finished computing the model PAW energy\n");
  PRINT_LINE_STAR
  PRINTF("\n");

  //==========================================================================
  // Tell everyone you are starting the forces

  PRINT_LINE_STAR
  PRINTF("Checking the forces of the model PAW energy\n");
  PRINT_LINE_DASH
  PRINTF("\n");

#ifdef _FORCECHECK_
  
  PRINTF("Enter the atom you want me to check:\n");
  int iii;
  scanf("%d", &iii);
  double deltau;
  ESTRUCT * edummy;

  for (int i=0; i<2; i++) {
	for (int j=0; j<3; j++) {
		switch (i) { 
			case 0: deltau = delta;  edummy = &energy_plus[j]; break; 
			case 1: deltau = -delta; edummy = &energy_minus[j]; break;
		} // end switch i
		switch (j) { 
			case 0: xd[iii] = x[iii] + deltau; break; 
			case 1: yd[iii] = y[iii] + deltau; break; 
			case 2: zd[iii] = z[iii] + deltau; break; 
		} // end switch j
   		computePAWreal(&atom_maps, &atom_pos_dummy, &cell, edummy);
   		computePAWlong(&atom_maps, &atom_pos_dummy, &cell, edummy, fgrid);
   		computePAWGrid(lmax, &atom_maps, &atom_pos_dummy, &cell, edummy, fgrid);
  		edummy->Etot0D.E     = edummy->ENN.E + edummy->EeN.E + edummy->EHar.E;
  		edummy->Etot0D.EGrid = edummy->ENN.EGrid + edummy->EeN.EGrid + edummy->EHar.EGrid;
  		edummy->Etot3D.E     = edummy->ENNshort.E + edummy->EeNshort.E + edummy->EHarshort.E + edummy->Elong.E - edummy->ENNselflong.E;
  		edummy->Etot3D.EGrid = edummy->ENNshort.EGrid + edummy->EeNshort.EGrid + edummy->EHarshort.EGrid 
								+ edummy->Elong.EGrid - edummy->ENNselflong.EGrid;
		switch (j) { 
			case 0: xd[iii] = x[iii]; break; 
			case 1: yd[iii] = y[iii]; break; 
			case 2: zd[iii] = z[iii]; break; 
		} // end switch j
	} // end for j
  }// end for i
  
  double * fdummy = new double [3];
  for (int j=0; j<3; j++) {
//	fdummy[j] = (energy_minus[j].Etot3D.EGrid -  energy_plus[j].Etot3D.EGrid)/(2.0*delta);
//	fdummy[j] = (energy_minus[j].Elong.E -  energy_plus[j].Elong.E)/(2.0*delta);
	fdummy[j] = (energy_minus[j].ENNshort.EGrid -  energy_plus[j].ENNshort.EGrid)/(2.0*delta);
  }
  PRINTF("%g %g %g : %g %g %g\n", fdummy[0], fdummy[1], fdummy[2], fxg[iii], fyg[iii], fzg[iii]);

#endif // _FORCECHECK_

  //========================================================================
  // Print out the forces

  PRINT_LINE_STAR;
  PRINTF(" Printing out forces\n");
  PRINT_LINE_DASH;
  for (int i=0; i<natm; i++) {
	PRINTF("fx0  [%d]: % 09.7f  |  % 09.7f  |  % 09.7f\n",i,atom_pos.fx0[i],atom_pos.fy0[i],atom_pos.fz0[i]);
	PRINTF("fx0g [%d]: % 09.7f  |  % 09.7f  |  % 09.7f\n",i,atom_pos.fx0g[i],atom_pos.fy0g[i],atom_pos.fz0g[i]);
	PRINTF("fx   [%d]: % 09.7f  |  % 09.7f  |  % 09.7f\n",i,atom_pos.fx[i],atom_pos.fy[i],atom_pos.fz[i]);
	PRINTF("fxg  [%d]: % 09.7f  |  % 09.7f  |  % 09.7f\n",i,atom_pos.fxg[i],atom_pos.fyg[i],atom_pos.fzg[i]);
  } // end for

  //==========================================================================
  // Tell everyone you are done
  PRINT_LINE_DASH
  PRINTF("Finished computing the model PAW forces\n");
  PRINT_LINE_STAR
  PRINTF("\n");
  return 0;

  //--------------------------------------------------------------------------
}//end routine
//==========================================================================
