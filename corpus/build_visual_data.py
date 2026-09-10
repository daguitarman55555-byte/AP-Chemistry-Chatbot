"""Original reproducible chemistry graph models, not measured or PhET-extracted data."""
from pathlib import Path
import math,json,sqlite3,collections
ROOT=Path(__file__).resolve().parent
R=8.314; F=96485; Kw=1e-14
def grid(a,b,n=201): return [a+(b-a)*j/(n-1) for j in range(n)]
def acid_h(C,Ka,Na=0):
    # Charge balance h+Na=Kw/h+C*Ka/(Ka+h), monotone in log h.
    lo=-16.; hi=1.
    for _ in range(100):
        mid=(lo+hi)/2; h=10**mid
        if h+Na-Kw/h-C*Ka/(Ka+h)>0: hi=mid
        else: lo=mid
    return 10**((lo+hi)/2)
def strong_h(excess):
    return (excess+math.sqrt(excess*excess+4*Kw))/2 if excess>=0 else 2*Kw/(math.sqrt(excess*excess+4*Kw)-excess)

rows=[]; model_defs={}
def put(family,i,topics,title,xlabel,ylabel,xs,ys,params,equation,assumptions):
    assert len(xs)==len(ys) and all(math.isfinite(v) for v in xs+ys)
    assert all(a<b for a,b in zip(xs,xs[1:]))
    rec=dict(id=f'{family}-{i:02d}',family_id=family,topic_ids=topics,title=title,
        x_label=xlabel,y_label=ylabel,parameters=params,equation=equation,assumptions=assumptions,
        provenance='original_model_generated',measured_data=False,phet_extracted=False,
        validation_status='finite_domain_and_model_invariants_checked; expert review pending',
        points=[dict(x=x,y=y) for x,y in zip(xs,ys)],
        student_visibility='exploration_only_unless_task_author_explicitly_approves_curve',
        interaction_contract=['select parameter set','inspect coordinate','compare prediction before curve reveal'],
        answer_leakage_policy='Do not supply task solution curves, hidden answers, or solved parameter values in guided mode.')
    rows.append(rec)
    model_defs[family]={k:v for k,v in rec.items() if k not in ('points','id','parameters')}

for i in range(1,101):
    n=.05+.005*i; T=280+i
    xs=grid(1,10); ys=[n*.08206*T/x for x in xs]
    put('gas_pv',i,['3.4'],'Pressure and volume','Volume (L)','Pressure (atm)',xs,ys,dict(n=n,T=T),'P=nRT/V','Ideal gas; fixed amount and Kelvin temperature.')
    xs=grid(200,500); ys=[n*.08206*x/5 for x in xs]
    put('gas_pt',i,['3.4','3.5'],'Pressure and temperature','Temperature (K)','Pressure (atm)',xs,ys,dict(n=n,V=5),'P=nRT/V','Ideal gas; fixed amount and volume.')
    xs=grid(200,500); ys=[n*.08206*x/1.0 for x in xs]
    put('gas_vt',i,['3.4'],'Volume and temperature','Temperature (K)','Volume (L)',xs,ys,dict(n=n,P=1),'V=nRT/P','Ideal gas; fixed amount and pressure.')
    c0=.15+i*.005; k=.002+i*.0001; xs=grid(0,100)
    ys=[max(0,c0-k*x) for x in xs]
    put('zero_order',i,['5.3'],'Zero-order depletion','Time (s)','Concentration (mol/L)',xs,ys,dict(c0=c0,k=k),'C=max(0,C0-kt)','Zero-order consumption until depletion; model stops at zero.')
    ys=[c0*math.exp(-k*x) for x in xs]
    put('first_order',i,['5.3'],'First-order decay','Time (s)','Concentration (mol/L)',xs,ys,dict(c0=c0,k=k),'C=C0 exp(-kt)','Single irreversible first-order process, fixed temperature.')
    ys=[1/(1/c0+k*x) for x in xs]
    put('second_order',i,['5.3'],'Second-order decay','Time (s)','Concentration (mol/L)',xs,ys,dict(c0=c0,k=k),'C=1/(1/C0+kt)','Rate convention -dC/dt=kC^2; k in L/(mol s).')
    xs=grid(.001,.2); order=1+(i%3); ys=[k*x**order for x in xs]
    put('rate_concentration',i,['5.2'],'Rate concentration dependence','Concentration (mol/L)','Rate (mol/(L s))',xs,ys,dict(k=k,order=order),'rate=k C^order','Hypothetical empirical rate law; k units depend on order.')
    Ea=30000+i*500; A=1e9; xs=grid(1/450,1/270); ys=[math.log(A)-Ea/R*x for x in xs]
    put('arrhenius',i,['5.5'],'Arrhenius model','Inverse temperature (1/K)','ln(k / 1 s^-1)',xs,ys,dict(Ea=Ea,A=A),'ln k=ln A-Ea/(RT)','Hypothetical first-order constant; Arrhenius parameters constant over range; enrichment quantitative model.')
    eps=500+i*25; xs=grid(0,.001); ys=[eps*x for x in xs]
    put('beer_lambert',i,['3.13'],'Absorbance calibration','Concentration (mol/L)','Absorbance',xs,ys,dict(epsilon=eps,b=1),'A=epsilon b c','Ideal dilute optical response; path length 1 cm; no blank offset.')
    ys=[10**(-eps*x) for x in xs]
    put('transmittance',i,['3.13'],'Transmission and concentration','Concentration (mol/L)','Transmittance fraction',xs,ys,dict(epsilon=eps,b=1),'transmittance=10^(-epsilon b c)','Ideal optical response; fraction, not percent.')
    Ka=10**(-3.5-i*.025); xs=grid(-6,-1); ys=[-math.log10(acid_h(10**x,Ka)) for x in xs]
    put('weak_acid_concentration',i,['8.3'],'Weak acid concentration sweep','log10(C / 1 M)','pH',xs,ys,dict(Ka=Ka,Kw=Kw),'Solve h=Kw/h+C Ka/(Ka+h)','Ideal monoprotic acid; includes water at 25 C; no added salt; no activity correction.')
    c=.04+i*.001; va=.025; cb=.1; veq=c*va/cb; xs=grid(0,veq*2*1000)
    hs=[acid_h(c*va/(va+x/1000),Ka,cb*x/1000/(va+x/1000)) for x in xs]
    ys=[-math.log10(h) for h in hs]
    assert all(a<=b+1e-8 for a,b in zip(ys,ys[1:]))
    for vol,h in zip(xs,hs):
        ct=c*va/(va+vol/1000); na=cb*vol/1000/(va+vol/1000)
        assert abs(h+na-Kw/h-ct*Ka/(Ka+h))<1e-10
    put('weak_acid_titration',i,['8.5','8.9'],'Weak acid titration model','Added base (mL)','pH',xs,ys,dict(Ca=c,Va_L=va,Cb=cb,Ka=Ka,Kw=Kw),'h+[Na+]=Kw/h+CT Ka/(Ka+h)','Ideal monoprotic acid and strong monovalent base; additive volumes; 25 C; full charge balance.')
    ys=[-math.log10(strong_h((c*va-cb*x/1000)/(va+x/1000))) for x in xs]
    assert abs(ys[100]-7)<1e-6
    put('strong_acid_titration',i,['8.5'],'Strong acid titration model','Added base (mL)','pH',xs,ys,dict(Ca=c,Va_L=va,Cb=cb,Kw=Kw),'h-Kw/h=(acid_moles-base_moles)/Vtotal','Ideal strong monoprotic acid and base; additive volumes; 25 C; includes water.')
    pk=-math.log10(Ka); xs=grid(0,14); ys=[1/(1+10**(pk-x)) for x in xs]
    put('acid_speciation',i,['8.7'],'Conjugate-base fraction','pH','Fraction A-',xs,ys,dict(pKa=pk),'alpha_A=1/(1+10^(pKa-pH))','Ideal single acid/conjugate-base pair at imposed pH; fraction is not concentration.')
    H=20000+i*500; S=80+i; xs=grid(200,600); ys=[(H-x*S)/1000 for x in xs]
    put('gibbs_temperature',i,['9.3'],'Standard Gibbs energy and temperature','Temperature (K)','Standard Gibbs energy (kJ/mol)',xs,ys,dict(H_J=H,S_J_K=S),'deltaGstandard=deltaHstandard-T deltaSstandard','Hypothetical constant enthalpy and entropy approximation over plotted range.')
    H=10000+i*300; Kref=2; xs=grid(270,350); ys=[math.log(Kref)-H/R*(1/x-1/298) for x in xs]
    put('equilibrium_temperature',i,['7.9','9.5'],'Equilibrium temperature model','Temperature (K)','ln K',xs,ys,dict(H_J=H,Kref=Kref,Tref=298),'ln K=ln Kref-deltaH/R*(1/T-1/Tref)','Constant reaction enthalpy; hypothetical system; quantitative enrichment model.')
    E0=.5+i*.005; xs=grid(-8,8); ys=[E0-R*298/(2*F)*x for x in xs]
    put('nernst',i,['9.10'],'Potential and reaction quotient','ln Q','Cell potential (V)',xs,ys,dict(E0=E0,n=2,T=298),'E=E0-RT/(nF) ln Q','Balanced model transfers two electrons; dimensionless Q; 25 C ideal model.')
    I=.1+i*.025; xs=grid(0,1200); ys=[I*x/F/2*63.55 for x in xs]
    put('electrolysis_mass',i,['9.11'],'Deposited mass model','Time (s)','Deposited mass (g)',xs,ys,dict(I_A=I,M=63.55,n=2),'mass=ItM/(nF)','Theoretical Cu2+ reduction; 100% current efficiency; no physical experiment instructions.')
    ks=(1+i*.1)*1e-10; xs=grid(-7,-2); ys=[2*ks/(10**x+math.sqrt(10**(2*x)+4*ks)) for x in xs]
    for x,y in zip(xs,ys): assert abs(y*(10**x+y)/ks-1)<1e-10
    put('common_ion',i,['7.12'],'Shared-ion solubility','log10(initial shared ion / 1 M)','Solubility (mol/L)',xs,ys,dict(Ksp=ks),'s(s+c_common)=Ksp','Ideal MX salt, 1:1 ions, no side reactions; free initial shared-ion concentration specified.')
    depth=.5+i*.02; xs=grid(.95,3); ys=[4*depth*(x**-12-x**-6) for x in xs]
    put('particle_potential',i,['2.2','3.1'],'Pair potential model','Separation / sigma','Energy / reference epsilon',xs,ys,dict(depth=depth),'U=4 depth (r^-12-r^-6)','Dimensionless Lennard-Jones illustration of attraction/repulsion; not a measured covalent-bond potential.')
    cp=2+i*.04; mass=100; xs=grid(0,8000); ys=[20+x/(mass*cp) for x in xs]
    put('sensible_heat',i,['6.4'],'Heating without phase change','Heat absorbed (J)','Temperature (C)',xs,ys,dict(m_g=mass,cp=cp,T0_C=20),'T=T0+q/(mc)','Hypothetical material with constant heat capacity; no phase change or heat loss.')
    ctotal=.2+i*.002; kf=.02; kr=.005+i*.0003; beq=ctotal*kf/(kf+kr); xs=grid(0,200); ys=[beq*(1-math.exp(-(kf+kr)*x)) for x in xs]
    assert all(0<=y<=ctotal for y in ys)
    put('reversible_relaxation',i,['7.1','7.8'],'Approach to equilibrium','Time (s)','Product concentration (mol/L)',xs,ys,dict(total=ctotal,kf=kf,kr=kr),'B=total*kf/(kf+kr)*(1-exp(-(kf+kr)t))','Closed ideal first-order A <-> B at fixed volume; initially all A; temperature fixed.')
    f=.1+i*.006; xs=grid(19,23); width=.04; ys=[f*math.exp(-.5*((x-20)/width)**2)+(1-f)*math.exp(-.5*((x-22)/width)**2) for x in xs]
    put('synthetic_mass_spectrum',i,['1.2'],'Two-isotope spectrum illustration','Mass (u)','Relative model signal',xs,ys,dict(fraction_mass20=f,width=width),'Two equal-width Gaussian peaks with abundance-weighted amplitudes','Artificial two-isotope element; broadened schematic, not measured instrument data; areas proportional to abundance.')
    qA=.4+i*.02; xs=grid(60,180); ys=[math.sqrt(max(0,2*qA*qA*(1+math.cos(x*math.pi/180)))) for x in xs]
    put('bond_dipole_sum',i,['2.7'],'Two-bond dipole sum','Bond angle (degrees)','Net dipole (relative units)',xs,ys,dict(each_bond_dipole=qA),'mu_net=sqrt(2 mu^2 (1+cos theta))','Vector sum of two equal bond dipoles; schematic, not a complete quantum molecular dipole calculation.')

dbdata=json.loads((ROOT/'chemistry_database.json').read_text())
sim_inputs=[
 ('acid-base-solutions','Acid-Base Solutions',['8.1','8.2','8.3'],'Compare strength and concentration; predict particle populations.'),
 ('beers-law-lab',"Beer's Law Lab",['3.13'],'Change path length or concentration; predict optical response.'),
 ('molarity','Molarity',['3.7'],'Relate solute amount, total volume, and concentration.'),
 ('concentration','Concentration',['3.7','3.10'],'Distinguish concentration change from saturation.'),
 ('ph-scale','pH Scale',['8.2'],'Explore logarithmic acidity and dilution.'),
 ('molecule-polarity','Molecule Polarity',['2.1','2.7'],'Predict bond-dipole and molecular-dipole behavior.'),
 ('gas-properties','Gas Properties',['3.4','3.5','3.6'],'Control gas variables and inspect collisions.'),
 ('build-an-atom','Build an Atom',['1.2','1.5','1.8'],'Distinguish identity, isotope, and ion charge.'),
 ('isotopes-and-atomic-mass','Isotopes and Atomic Mass',['1.2'],'Connect isotope abundance and average mass.'),
 ('atomic-interactions','Atomic Interactions',['2.2','3.1'],'Explore separation, forces, and potential energy.'),
 ('states-of-matter','States of Matter',['3.2','3.3'],'Connect particle motion and bulk phase behavior.'),
 ('balancing-chemical-equations','Balancing Chemical Equations',['4.3','4.5'],'Conserve element counts through a reaction.'),
 ('reactants-products-and-leftovers','Reactants, Products and Leftovers',['4.5'],'Predict limiting amounts and residual reactants.'),
 ('diffusion','Diffusion',['3.5'],'Explore spreading and mixing at particle scale.'),
 ('energy-forms-and-changes','Energy Forms and Changes',['6.1','6.3'],'Track energy transfer; supplement, not full calorimetry course.'),
 ('molecule-shapes-basics','Molecule Shapes: Basics',['2.7'],'Relate electron domains and molecular shape; introductory scope.'),
 ('build-a-molecule','Build a Molecule',['2.5','4.3'],'Connect atoms, formulas, and molecule construction.')]
sims=[dict(id=slug,title=title,topic_ids=ts,teaching_use=use,repository_url='https://github.com/phetsims/'+slug,
    verification='official repository opened; runtime interaction not tested',runtime_verified=False,
    preferred_integration='link to official repository and its published simulation link',
    regular_binary_license='CC BY-NC 4.0 per current PhET licensing page; preserve attribution and branding',
    license_url='https://phet.colorado.edu/en/licensing',source_code_license='per-repository; not inferred from binary license',
    phet_io_access='separately licensed; not acquired',bundled=False,
    can_read_state=False,can_control_state=False,limitations='Ordinary embedding is not an instrumentation API; may expose answer-relevant values.',
    checked_on='2026-09-10') for slug,title,ts,use in sim_inputs]
for filename,obj in [('graph_models.json',list(model_defs.values())),('phet_catalog.json',sims)]:
    (ROOT/filename).write_text(json.dumps(obj,indent=2))
(ROOT/'graph_datasets.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows))

# A target is not counted as achieved by filling placeholder rows or varying numbers.
coverage=[]
for t in dbdata['topics']:
    qs=[q for q in dbdata['questions'] if q['topic_id']==t['id']]
    families=sorted(set(q['family_id'] for q in qs))
    coverage.append(dict(topic_id=t['id'],label=t['label'],required_distinct_types=200,
        authored_family_count=len(families),expert_validated_distinct_types=0,
        minimum_additional_authored_types=max(0,200-len(families)),
        requirement_met=False,authored_families=families,
        definition='Different chemistry reasoning structure; renumbering, numeric variants, or cosmetic wording do not count.',
        graph_families=[m['family_id'] for m in model_defs.values() if t['id'] in m['topic_ids']],
        phet_ids=[s['id'] for s in sims if t['id'] in s['topic_ids']]))
(ROOT/'coverage_200_types_per_topic.json').write_text(json.dumps(coverage,indent=2))
con=sqlite3.connect(ROOT/'chemistry.sqlite')
for table in ('graph_models','graph_datasets','phet_simulations','coverage_targets'): con.execute(f'DROP TABLE IF EXISTS {table}')
con.execute('CREATE TABLE graph_models(id TEXT PRIMARY KEY,data_json TEXT)')
con.execute('CREATE TABLE graph_datasets(id TEXT PRIMARY KEY,family_id TEXT REFERENCES graph_models(id),data_json TEXT)')
con.execute('CREATE TABLE phet_simulations(id TEXT PRIMARY KEY,data_json TEXT)')
con.execute('CREATE TABLE coverage_targets(topic_id TEXT PRIMARY KEY REFERENCES topics(id),target INTEGER,authored_types INTEGER,validated_types INTEGER,met INTEGER,data_json TEXT)')
for k,v in model_defs.items(): con.execute('INSERT INTO graph_models VALUES(?,?)',(k,json.dumps(v)))
for r in rows: con.execute('INSERT INTO graph_datasets VALUES(?,?,?)',(r['id'],r['family_id'],json.dumps(r)))
for r in sims: con.execute('INSERT INTO phet_simulations VALUES(?,?)',(r['id'],json.dumps(r)))
for r in coverage: con.execute('INSERT INTO coverage_targets VALUES(?,?,?,?,?,?)',(r['topic_id'],200,r['authored_family_count'],0,0,json.dumps(r)))
con.commit(); con.close()
summary=dict(graph_families=len(model_defs),datasets=len(rows),points=sum(len(r['points']) for r in rows),
    measured_datasets=0,phet_catalog_entries=len(sims),bundled_phet_simulations=0,
    required_distinct_types=18200,topics_meeting_200_types=0,existing_authored_families=sum(r['authored_family_count'] for r in coverage))
(ROOT/'visual_validation_report.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
