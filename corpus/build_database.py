"""Rebuild the original AP Chemistry study corpus. Python 3 standard library only."""
from pathlib import Path
import math, json, sqlite3, hashlib, collections

ROOT=Path(__file__).resolve().parent
DATE='2026-09-10'
CED='https://apcentral.collegeboard.org/media/pdf/ap-chemistry-course-and-exam-description.pdf'
ARCHIVE='https://apcentral.collegeboard.org/courses/ap-chemistry/exam/past-exam-questions'
R=8.314; F=96485; RGAS=0.08206

units=[
 (1,'Atoms and periodic behavior',7,9,[]),
 (2,'Bonding and compound structure',7,9,[1]),
 (3,'Bulk matter, solutions, and spectra',18,22,[1,2]),
 (4,'Reaction accounting',7,9,[1,2,3]),
 (5,'Reaction speed and mechanisms',7,9,[3,4]),
 (6,'Heat and enthalpy',7,9,[3,4]),
 (7,'Reversible reactions',7,9,[3,4,5]),
 (8,'Proton transfer and buffers',11,15,[4,7]),
 (9,'Free energy and electrical chemistry',7,9,[4,6,7])]

topics=[]; questions=[]; solutions=[]; hints=[]; checks=[]
def add(qid,topic,family,prompt,answer,steps,hint_list,misconception,params=None,unit=None,residual=None,answer_kind='numeric'):
    questions.append(dict(id=qid,topic_id=topic,family_id=family,origin='original',prompt=prompt,
        answer_kind=answer_kind,science_practices=[5] if answer_kind=='numeric' else [6],
        difficulty='un calibrated'.replace(' ',''),exam_authenticity='not an official AP item',
        review_status='algebra_checked_not_expert_reviewed' if residual is not None else 'authored_not_expert_reviewed',
        parameters=params or {},misconception=misconception))
    solutions.append(dict(question_id=qid,answer=answer,answer_unit=unit,steps=steps,
        relative_tolerance=0.005 if answer_kind=='numeric' else None,
        absolute_tolerance=0.005 if unit=='pH' else (1e-14 if answer_kind=='numeric' else None),
        precision_policy='Retain guard digits; numeric tolerance is not a significant-figure grade.',
        access='teacher_or_backend_only'))
    for i,h in enumerate(hint_list,1): hints.append(dict(question_id=qid,level=i,text=h,reveals_final_answer=False))
    if residual is not None:
        assert math.isfinite(answer),qid
        assert abs(residual)<1e-8,(qid,residual)
        checks.append(dict(question_id=qid,check='independent_relation_or_inverse_substitution',residual=residual,status='pass'))

for line in (ROOT/'concepts.txt').read_text().splitlines():
    tid,label,prompt,explanation,misconception,hint=line.split('|')
    topics.append(dict(id=tid,unit_id=int(tid.split('.')[0]),label=label,source_url=CED,
                       coverage='one conceptual seed; not exhaustive essential-knowledge coverage',
                       mapping_status='topic-number aligned; expert audit pending'))
    add('C-'+tid,tid,'concept-'+tid,prompt,explanation,[explanation],
        ['What principle would you use to explain this?',hint],misconception,answer_kind='explanation')

def nadd(family,i,topic,prompt,ans,unit,steps,hints_,mistake,params,residual):
    add(f'{family}-{i:02d}',topic,family,prompt+' Report a numerical answer with units where applicable.',
        ans,steps+[f'Numerical result: {ans:.8g} {unit or ""}.'],hints_,mistake,params,unit,residual)

for i in range(1,26):
    # Each family uses distinct displayed inputs, bounded to its model's domain.
    m=1.25+i*0.37; M=58.44; a=m/M
    nadd('moles',i,'1.1',f'A NaCl sample has mass {m:.2f} g. Use molar mass 58.44 g/mol. Find its amount in moles.',a,'mol',
         ['Use n=m/M.',f'n=({m:.2f} g)/(58.44 g/mol).'],['Which conversion connects mass and moles?','Arrange the units so grams cancel.'],
         'Multiplying mass by molar mass.',dict(m=m,M=M),(a*M-m)/m)
    f=0.2+i*.02; a=20*f+22*(1-f)
    nadd('isotopes',i,'1.2',f'A hypothetical element has isotope masses 20.00 u and 22.00 u. Their fractional abundances are {f:.2f} and {1-f:.2f}. Find its mean atomic mass.',a,'u',
         ['Weight each isotope mass by its fraction.',f'mean=20.00*{f:.2f}+22.00*{1-f:.2f}.'],['Are the two isotopes equally abundant?','Multiply each mass by its population fraction before adding.'],
         'Taking an unweighted mean.',dict(f=f),(22-a)/2-f)
    # Hypothetical Lewis bookkeeping cases, explicitly not asserted to describe stable molecules.
    if i <= 3:
        v=5; nonbond=2; shared=2+2*(i%3); a=v-nonbond-shared/2
        nadd('formal_charge',i,'2.6',f'In a hypothetical Lewis drawing, a nitrogen atom has 2 nonbonding electrons and {shared} bonding electrons shared with neighbors. Nitrogen has 5 valence electrons. Find its formal charge.',a,'elementary-charge units',
             ['Formal charge = valence - nonbonding - half of bonding electrons.',f'FC=5-2-{shared}/2.'],['Which electrons are assigned fully to this atom?','Assign half of each bonding pair to nitrogen.'],
             'Subtracting all shared electrons.',dict(v=v,nonbond=nonbond,shared=shared),a+nonbond+shared/2-v)
    n=.1+i*.013; T=280+i*2; V=3+i*.17; a=n*RGAS*T/V
    nadd('ideal_gas',i,'3.4',f'An ideal gas has n={n:.3f} mol, T={T} K, and V={V:.2f} L. Use R=0.08206 L atm/(mol K). Find pressure.',a,'atm',
         ['Use PV=nRT and isolate P.',f'P={n:.3f}*0.08206*{T}/{V:.2f}.'],['Which gas variables are supplied?','Rearrange PV=nRT before substituting.'],
         'Putting volume in the numerator.',dict(n=n,T=T,V=V),a*V/(n*RGAS*T)-1)
    c=.02+i*.003; v1=10+i; v2=150+i*2; a=c*v1/v2
    nadd('dilution',i,'3.7',f'A solution initially has concentration {c:.3f} mol/L. An aliquot of {v1} mL is diluted to a final volume of {v2} mL without reaction. Find final concentration.',a,'mol/L',
         ['Solute amount is conserved: c1*V1=c2*V2.',f'c2={c:.3f}*{v1}/{v2}.'],['What remains constant when only solvent is added?','Use the final total volume, not the added solvent volume.'],
         'Treating final volume as added volume.',dict(c=c,v1=v1,v2=v2),a*v2/(c*v1)-1)
    lam=410+i*7; a=6.626e-34*2.998e8/(lam*1e-9)
    nadd('photon',i,'3.12',f'A photon has wavelength {lam} nm. Use h=6.626e-34 J s and c=2.998e8 m/s. Find its energy.',a,'J',
         ['Convert nm to m by multiplying by 1e-9.','Use E=hc/lambda.',f'E=(6.626e-34)*(2.998e8)/({lam}e-9).'],
         ['Which relationship links energy to frequency?','Combine c=lambda*frequency with E=h*frequency.'],
         'Using nanometers as meters.',dict(lam_nm=lam),a*(lam*1e-9)/(6.626e-34*2.998e8)-1)
    ab=.1+i*.021; eps=1250; path=1.0; a=ab/(eps*path)
    nadd('absorbance',i,'3.13',f'A dilute sample obeys Beer-Lambert behavior with absorbance {ab:.3f}, path length 1.00 cm, and absorptivity 1250 L/(mol cm). Find concentration.',a,'mol/L',
         ['Use A=epsilon*b*c.','Isolate c=A/(epsilon*b).',f'c={ab:.3f}/(1250*1.00).'],['Which factors multiply to give absorbance?','Divide out both path length and absorptivity.'],
         'Treating absorbance as a percentage.',dict(A=ab,eps=eps,b=path),a*eps*path/ab-1)
    na=.02+i*.002; nb=.018+i*.0007; a=min(na/2,nb)
    nadd('limiting',i,'4.5',f'For the idealized complete reaction 2 A + B -> A2B, initial amounts are {na:.4f} mol A and {nb:.4f} mol B. Find the maximum amount of A2B.',a,'mol',
         ['A can supply n(A)/2 reaction extents; B can supply n(B).',f'Compare {na:.4f}/2 with {nb:.4f}.','Use the smaller extent; product coefficient is one.'],
         ['How many A particles are needed per product?','Compare available moles divided by their reaction coefficients.'],
         'Comparing raw moles without coefficients.',dict(na=na,nb=nb),min(na-2*a,nb-a))
    ca=.02+i*.002; va=20+i; cb=.1; a=ca*va/cb
    nadd('titration',i,'4.6',f'In a theoretical 1:1 acid-base titration, {va} mL of {ca:.3f} mol/L monoprotic acid reaches equivalence with a {cb:.3f} mol/L base. Find base volume in mL.',a,'mL',
         ['At equivalence n(acid)=n(base).','Using matching volume units gives ca*Va=cb*Vb.',f'Vb={ca:.3f}*{va}/0.100.'],
         ['What must be equal at 1:1 equivalence?','Use moles rather than assuming equal volumes.'],
         'Equating volumes directly.',dict(ca=ca,va=va,cb=cb),cb*a/(ca*va)-1)
    k=.002+i*.0004; t=20+i*3; c0=.25; a=c0*math.exp(-k*t)
    nadd('first_order',i,'5.3',f'A follows first-order decay with k={k:.4f} s^-1 and initial concentration 0.250 mol/L. Find its concentration after {t} s.',a,'mol/L',
         ['ln([A]t/[A]0)=-kt.','Exponentiate: [A]t=[A]0*exp(-kt).',f'[A]t=0.250*exp(-{k:.4f}*{t}).'],
         ['Which integrated law matches first order?','Isolate the concentration after exponentiating.'],
         'Using a linear concentration decrease.',dict(k=k,t=t,c0=c0),math.log(a/c0)+k*t)
    a=math.log(2)/k
    nadd('half_life',i,'5.3',f'A first-order process has k={k:.4f} s^-1. Find its half-life.',a,'s',
         ['At half-life [A]t/[A]0=1/2.','Set ln(1/2)=-k*t and solve.',f't=ln(2)/{k:.4f}.'],
         ['What fraction remains after one half-life?','Insert that fraction into the first-order integrated law.'],
         'Multiplying k by ln(2).',dict(k=k),math.exp(-k*a)-.5)
    k2=.01+i*.001; c0=.2; t=40+i*4; a=1/(1/c0+k2*t)
    nadd('second_order',i,'5.3',f'A follows rate=-d[A]/dt=k[A]^2 with k={k2:.3f} L/(mol s), [A]0=0.200 mol/L, and t={t} s. Find [A]t.',a,'mol/L',
         ['Use 1/[A]t=1/[A]0+kt.',f'[A]t=1/(1/0.200+{k2:.3f}*{t}).'],
         ['Which concentration transformation is linear for this order?','Solve for the reciprocal first, then invert.'],
         'Forgetting the final reciprocal.',dict(k=k2,c0=c0,t=t),((1/a-1/c0)-k2*t))
    mass=80+i*2; cp=4.18; dt=1+i*.12; a=mass*cp*dt
    nadd('heat',i,'6.4',f'A modeled sample has mass {mass} g, specific heat 4.18 J/(g K), and temperature increase {dt:.2f} K without phase change. Find heat absorbed.',a,'J',
         ['Use q=m*c*deltaT; the sign is positive for warming.',f'q={mass}*4.18*{dt:.2f}.'],
         ['Is the sample gaining or losing heat?','Use the temperature difference rather than the final temperature.'],
         'Using final temperature in place of its change.',dict(m=mass,c=cp,dt=dt),a/(mass*cp)-dt)
    n=.04+i*.002; q=-(1100+i*31); a=q/n/1000
    nadd('molar_enthalpy',i,'6.6',f'At constant pressure, reaction of {n:.3f} mol of the specified reactant releases {abs(q)} J. There is no other work than pressure-volume work. Find reaction enthalpy per mole of that reactant.',a,'kJ/mol',
         ['Heat released means negative system heat.','Divide by reacted moles and convert J to kJ.',f'deltaH=({q})/{n:.3f}/1000.'],
         ['Which sign represents energy leaving the system?','Convert the total heat to energy per reacted mole.'],
         'Reporting a positive sign for released heat.',dict(n=n,q=q),a*n*1000/q-1)
    aa=.1+i*.002; bb=.2+i*.003; a=bb/aa
    nadd('equilibrium_ratio',i,'7.4',f'For ideal dilute A(aq) <-> B(aq), measured equilibrium concentrations are [A]={aa:.3f} M and [B]={bb:.3f} M. Find K using concentrations normalized to 1 M.',a,'dimensionless',
         ['Both stoichiometric coefficients are one.','K=activity(B)/activity(A), approximated by [B]/[A].',f'K={bb:.3f}/{aa:.3f}.'],
         ['Which side belongs in the numerator?','Use the equilibrium values rather than initial values.'],
         'Taking reactant over product.',dict(A=aa,B=bb),a*aa/bb-1)
    K=.2+i*.15; total=.3; a=K*total/(1+K)
    nadd('equilibrium_extent',i,'7.7',f'An ideal dilute A(aq) <-> B(aq) mixture initially contains only 0.300 M A. K={K:.2f}. Volume is constant. Find equilibrium [B].',a,'mol/L',
         ['Let [B]=x, then [A]=0.300-x.','K=x/(0.300-x).','Rearrange to x=0.300*K/(1+K).'],
         ['How does forming B change A?','Express both equilibrium concentrations using one unknown.'],
         'Holding [A] fixed at its initial value.',dict(K=K,total=total),a/(total-a)-K)
    ks=(1+i*.3)*1e-10; a=math.sqrt(ks)
    nadd('ksp_11',i,'7.11',f'A hypothetical salt MX(s) <-> M+(aq)+X-(aq) has Ksp={ks:.8g}. Assume ideal dilute pure water, no shared ions, and no side reactions. Find molar solubility.',a,'mol/L',
         ['Each dissolved mole produces one mole of each ion.','Ksp=s*s, so s=sqrt(Ksp).'],
         ['What are the two ion concentrations in terms of solubility?','Substitute them into the solubility-product expression.'],
         'Setting solubility equal to Ksp.',dict(Ksp=ks),a*a/ks-1)
    ks=(1+i*.2)*1e-12; a=(ks/4)**(1/3)
    nadd('ksp_12',i,'7.11',f'A hypothetical MX2 salt dissociates into M2+ and 2 X-. Ksp={ks:.8g}. Assume ideal dilute pure water and no side reactions. Find molar solubility.',a,'mol/L',
         ['If solubility is s, [M2+]=s and [X-]=2s.','Ksp=s*(2s)^2=4s^3.','s=(Ksp/4)^(1/3).'],
         ['How many X- ions come from each formula unit?','Apply the anion coefficient as an exponent too.'],
         'Using s squared for every salt.',dict(Ksp=ks),4*a**3/ks-1)
    c=(1+i*.23)*1e-3; a=-math.log10(c)
    nadd('strong_acid',i,'8.2',f'A theoretical dilute fully dissociated monoprotic acid has concentration {c:.8g} M at 25 C. Neglect water autoionization and activity corrections. Find pH.',a,'pH',
         ['Complete dissociation gives [H3O+]=acid concentration.','pH=-log10([H3O+]/1 M).',f'pH=-log10({c:.8g}).'],
         ['How many hydronium ions arise per acid molecule?','Apply the negative base-ten logarithm.'],
         'Using natural log instead of base ten.',dict(c=c),10**(-a)/c-1)
    ka=1.6e-5; c=.04+i*.004
    x=2*ka*c/(math.sqrt(ka*ka+4*ka*c)+ka); a=-math.log10(x)
    nadd('weak_acid',i,'8.3',f'A hypothetical monoprotic weak acid HA has Ka=1.60e-5 and initial concentration {c:.3f} M at 25 C. Initially no conjugate base is added. Neglect water autoionization and activity corrections. Find pH without the small-x approximation.',a,'pH',
         ['Let x=[H3O+]=[A-], leaving [HA]=C-x.','Ka=x^2/(C-x); solve x^2+Ka*x-Ka*C=0.',
          'Choose the positive physical root; a stable formula is x=2*Ka*C/(sqrt(Ka^2+4*Ka*C)+Ka).',f'x={x:.8g} M; pH=-log10(x).'],
         ['Which species change by the same amount?','Write the acid equilibrium expression using one unknown.','Choose a root between zero and the initial acid concentration.'],
         'Assuming full dissociation for a weak acid.',dict(Ka=ka,C=c),x*x/(c-x)/ka-1)
    pk=4.8; acid=.08; base=.025+i*.004; a=pk+math.log10(base/acid)
    nadd('buffer',i,'8.9',f'An ideal buffer contains {acid:.3f} M HA and {base:.3f} M A-, with pKa=4.80. Equilibrium changes to these concentrations are negligible. Find pH.',a,'pH',
         ['Use pH=pKa+log10([A-]/[HA]).',f'pH=4.80+log10({base:.3f}/0.080).'],
         ['Which species is the conjugate base?','Place conjugate base over acid in the ratio.'],
         'Inverting the buffer ratio.',dict(pKa=pk,acid=acid,base=base),10**(a-pk)*acid/base-1)
    H=25000+i*700; S=95+i; T=298; a=(H-T*S)/1000
    nadd('gibbs',i,'9.3',f'At 298 K a hypothetical reaction has standard deltaH={H/1000:.3f} kJ/mol and standard deltaS={S} J/(mol K). Find standard deltaG.',a,'kJ/mol',
         ['Use deltaG=deltaH-T*deltaS.','Convert enthalpy to J/mol before subtraction.',f'deltaG=({H}-298*{S})/1000 kJ/mol.'],
         ['Do the enthalpy and entropy terms use compatible energy units?','Multiply entropy by absolute temperature before subtracting.'],
         'Mixing joules and kilojoules.',dict(H=H,S=S,T=T),(a*1000+T*S-H)/H)
    dg=-2000-i*400; T=298; a=math.exp(-dg/(R*T))
    nadd('gibbs_K',i,'9.5',f'A hypothetical reaction has standard deltaG={dg} J/mol at 298 K. Use R=8.314 J/(mol K). Find its dimensionless equilibrium constant.',a,'dimensionless',
         ['deltaGstandard=-RT*ln(K).','K=exp(-deltaGstandard/(RT)).',f'K=exp(-({dg})/(8.314*298)).'],
         ['Should a negative standard Gibbs energy correspond to K above or below one?','Isolate ln(K) before exponentiating.'],
         'Using a base-ten exponential with a natural-log formula.',dict(dg=dg,T=T),(-R*T*math.log(a)-dg)/abs(dg))
    e=.2+i*.025; ne=2; a=-ne*F*e/1000
    nadd('cell_energy',i,'9.9',f'A modeled redox reaction transfers 2 mol electrons per mole of reaction and has standard cell potential {e:.3f} V. Use F=96485 C/mol. Find standard Gibbs energy per mole of reaction.',a,'kJ/mol',
         ['Use deltaGstandard=-n*F*Estandard.','A volt is a joule per coulomb.',f'deltaGstandard=-2*96485*{e:.3f}/1000 kJ/mol.'],
         ['How does electrical potential relate to energy per charge?','Track the negative sign and convert J to kJ.'],
         'Omitting the transferred electron count.',dict(E=e,n=ne),(-a*1000/(ne*F)-e))
    q=.3+i*.4; e0=.85; T=298; ne=2; a=e0-R*T/(ne*F)*math.log(q)
    nadd('nernst',i,'9.10',f'A hypothetical cell has Estandard=0.850 V, n=2, T=298 K, and dimensionless Q={q:.2f}. Use R=8.314 J/(mol K) and F=96485 C/mol. Find E.',a,'V',
         ['E=Estandard-(RT/(nF))*ln(Q).',f'E=0.850-(8.314*298/(2*96485))*ln({q:.2f}).'],
         ['Is Q equal to one?','Use a natural logarithm with the stated RT/(nF) coefficient.'],
         'Using log10 without changing the coefficient.',dict(Q=q,E0=e0,T=T,n=ne),math.exp((e0-a)*ne*F/(R*T))/q-1)
    current=.2+i*.03; t=100+i*13; M=63.55; ne=2; a=current*t/F/ne*M
    nadd('electrolysis',i,'9.11',f'For a theoretical Cu2+ + 2 e- -> Cu calculation, current is {current:.2f} A for {t} s with 100% current efficiency. Use F=96485 C/mol and Cu molar mass 63.55 g/mol. Find deposited mass.',a,'g',
         ['Charge=current*time.','Moles electrons=charge/F.','Moles Cu=(moles electrons)/2.',f'mass=({current:.2f}*{t}/96485/2)*63.55.'],
         ['What quantity is current multiplied by time?','Convert charge to moles of electrons, then use the half-reaction ratio.'],
         'Treating moles of electrons as moles of copper.',dict(I=current,t=t,M=M,n=ne),a/M*ne*F/(current*t)-1)

lab_seeds=[
 ('L-01','3.13',2,'A hypothetical absorbance dataset has two candidate calibration curves: one uses standards in the same solvent as the unknown, the other a different solvent. Which is the better starting choice, and why?',
  'Use the same-solvent calibration, provided other conditions also match. Solvent can affect the absorbing species and optical background; matching it reduces a confounding variable.',
  'Which experimental condition should be held constant?', 'Assuming any calibration curve is transferable.'),
 ('L-02','6.4',2,'A hypothetical calorimetry calculation ignores a cup that warms alongside the solution. If the reaction releases heat, does ignoring the cup underestimate or overestimate the magnitude of reaction heat? Explain.',
  'It underestimates the magnitude. Both solution and cup absorb energy, so reaction heat is the negative of their combined heat; counting only the solution misses a positive contribution.',
  'Which objects gain energy in the stated model?', 'Ignoring apparatus heat capacity without checking its effect.'),
 ('L-03','3.13',3,'A hypothetical calibration table gives concentration in mM: 0, 1, 2, 3; absorbance: 0.02, 0.17, 0.32, 0.47. Describe labeled graph axes and write a linear calibration equation. Do not force the intercept to zero.',
  'Put concentration c in mM on the horizontal axis and dimensionless absorbance A on the vertical axis. The slope is (0.47-0.02)/3=0.15 per mM and the intercept is 0.02, so A=0.15*c+0.02.',
  'Which variable is controlled, and what absorbance occurs at zero concentration?', 'Automatically forcing every calibration through zero.'),
 ('L-04','4.3',3,'A closed hypothetical particle model begins with six A atoms and two B2 molecules. Reaction forms only AB molecules until B2 is exhausted. Describe the final particle inventory and verify conservation.',
  'Four AB molecules and two unreacted A atoms remain. The final A count is 4+2=6 and the final B count is 4, matching the initial two B2 molecules.',
  'Count atoms separately before assigning product molecules.', 'Conserving molecule count instead of atom count.'),
 ('L-05','5.2',4,'In hypothetical initial-rate data, doubling [A] at fixed [B] doubles rate; doubling [B] at fixed [A] quadruples rate. Determine the rate law and explain the comparison.',
  'The A order is one because 2^m=2; the B order is two because 2^n=4. The supported law is rate=k[A][B]^2 for these conditions.',
  'Compare runs where only one concentration changes.', 'Changing two variables at once when inferring an order.'),
 ('L-06','3.8',1,'An idealized diagram represents one dissolved sodium sulfate formula unit. Describe the ions and the atom and charge counts it must preserve.',
  'It contains two Na+ ions and one SO4^2- ion. The sulfate ion retains one sulfur and four oxygen atoms; total charge is 2-2=0.',
  'Does a polyatomic ion need to be split into individual atoms?', 'Splitting an intact polyatomic ion into free atoms.'),
 ('L-07','4.6',2,'In hypothetical titration data, every recorded delivered base volume is 0.40 mL larger than its true value. If known base concentration and measured acid volume are used to calculate unknown acid concentration for a 1:1 reaction, what direction is the bias?',
  'The calculated acid concentration is too high. It is proportional to recorded delivered base volume through ca=cb*Vb/Va, so a positive Vb error raises ca.',
  'Which measured quantity appears in the numerator of the concentration calculation?', 'Calling every experimental error random.'),
 ('L-08','5.3',3,'A hypothetical first-order dataset gives [A]/[A]0 values 1, 1/2, 1/4 at times 0, 10, 20 seconds. Describe a linear plot and calculate its slope with units.',
  'Plot ln([A]/[A]0) against time in seconds. The slope is ln(1/2)/10=-0.0693147 s^-1, and equals -k. The zero-time ordinate is zero.',
  'Which transformation converts repeated multiplication into equal increments?', 'Using concentration rather than its logarithm for a first-order linear plot.'),
]
for qid,topic,practice,prompt,answer,hint,misconception in lab_seeds:
    add(qid,topic,qid,prompt,answer,[answer],['Identify the measurements and the quantity being inferred.',hint],misconception,answer_kind='explanation')
    questions[-1]['science_practices']=[practice]

exam_sets=[]; exam_items=[]
for year in range(2023,2027):
    frq=f'https://apcentral.collegeboard.org/media/pdf/ap{str(year)[2:]}-frq-chemistry.pdf'
    sg=f'https://apcentral.collegeboard.org/media/pdf/ap{str(year)[2:]}-sg-chemistry.pdf' if year<2026 else None
    exam_sets.append(dict(id=f'CB-{year}-public-FRQ',year=year,section='FRQ',form='publicly linked set',
        questions_url=frq,scoring_url=sg,verified_on=DATE,source_index=ARCHIVE,
        verification='PDF opened with web tool',scoring_status='PDF opened' if sg else 'not linked on inspected index',
        rights='College Board copyright; external reference only; no redistribution or training grant inferred',
        stored_exam_text=False,stored_worked_solutions=False))
    for q in range(1,8):
        exam_items.append(dict(id=f'CB-{year}-Q{q}',exam_set_id=f'CB-{year}-public-FRQ',question_number=q,
           length='long' if q<=3 else 'short',max_points=10 if q<=3 else 4,
           topic_mapping_status='not yet annotated',solution_status='official source link only' if sg else 'not available in catalog',
           prompt_text=None,worked_solution=None))

archive_audit=[]
for year in range(1999,2023):
    for kind in ('frq','sg'):
        checked=year in (2019,2021,2022)
        status=('redirected_to_general_archive' if not(kind=='frq' and year in (2021,2022)) else 'web_open_failed') if checked else 'not_checked'
        archive_audit.append(dict(year=year,resource_kind=kind,status=status,
            attempted_url=f'https://apcentral.collegeboard.org/media/pdf/ap{str(year)[2:]}-{kind}-chemistry.pdf' if checked else None,
            notes='A failed/redirected URL does not prove no authorized copy exists. All forms and pre-1999 history remain unassessed.'))

sources=[
 dict(id='curriculum',url=CED,purpose='Topic numbering and course scope',checked_on=DATE),
 dict(id='course',url='https://apcentral.collegeboard.org/courses/ap-chemistry',purpose='Unit weighting and science practices',checked_on=DATE),
 dict(id='exam_format',url='https://apcentral.collegeboard.org/courses/ap-chemistry/exam',purpose='Exam format',checked_on=DATE),
 dict(id='archive',url=ARCHIVE,purpose='Released resource inventory',checked_on=DATE),
 dict(id='corrections',url='https://apcentral.collegeboard.org/media/pdf/ap-chemistry-course-and-exam-description-clarifications.pdf',purpose='June 2026 updates and moved resources',checked_on=DATE),
 dict(id='release_changes',url='https://apcentral.collegeboard.org/courses/past-exam-questions/release-update',purpose='2027 release timing and unreleased forms',checked_on=DATE),
]
for slug in ['14-2-ph-and-poh','12-4-integrated-rate-laws','16-4-free-energy','17-4-potential-free-energy-and-equilibrium']:
    sources.append(dict(id='openstax-'+slug,url='https://openstax.org/books/chemistry-2e/pages/'+slug,
                        purpose='Independent chemistry relationship reference; no textbook questions copied',checked_on=DATE))

metadata=dict(schema_version='1.0.0',build_date=DATE,scope='Curriculum seed plus original practice and official exam reference catalog',
    complete_past_exam_database=False,complete_learning_objective_database=False,
    official_exam_questions_copied=0,official_exam_worked_solutions_authored=0,
    warning='Not a production-validated tutor. No promise of AP score or error-free chemistry.',
    constants=dict(R_J_mol_K=R,R_L_atm_mol_K=RGAS,F_C_mol=F),
    holdout_policy='Split by family before sampling variants; official questions must stay out of model-training data without rights clearance.')

data=dict(metadata=metadata,units=[dict(id=u,title=t,mcq_min_pct=lo,mcq_max_pct=hi,recommended_prerequisite_units=p) for u,t,lo,hi,p in units],
          topics=topics,questions=questions,solutions=solutions,hints=hints,exam_sets=exam_sets,exam_items=exam_items,
          archive_audit=archive_audit,sources=sources,validation_checks=checks)
assert len(topics)==91
assert len({q['id'] for q in questions})==len(questions)
assert len({q['prompt'] for q in questions})==len(questions)
assert set(q['topic_id'] for q in questions)==set(t['id'] for t in topics)
assert len(checks)==628
(ROOT/'chemistry_database.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
for name in ['topics','questions','solutions','hints','exam_sets','exam_items','archive_audit','sources']:
    (ROOT/(name+'.jsonl')).write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in data[name]))

dbpath=ROOT/'chemistry.sqlite'
if dbpath.exists(): dbpath.unlink()
db=sqlite3.connect(dbpath)
db.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE units(id INTEGER PRIMARY KEY, title TEXT NOT NULL, mcq_min_pct INTEGER, mcq_max_pct INTEGER, prerequisites_json TEXT);
CREATE TABLE topics(id TEXT PRIMARY KEY, unit_id INTEGER REFERENCES units(id), label TEXT, data_json TEXT);
CREATE TABLE questions(id TEXT PRIMARY KEY, topic_id TEXT REFERENCES topics(id), family_id TEXT, prompt TEXT, origin TEXT, review_status TEXT, data_json TEXT);
CREATE TABLE solutions(question_id TEXT PRIMARY KEY REFERENCES questions(id), data_json TEXT NOT NULL);
CREATE TABLE hints(question_id TEXT REFERENCES questions(id), level INTEGER, text TEXT, PRIMARY KEY(question_id,level));
CREATE TABLE exam_sets(id TEXT PRIMARY KEY, year INTEGER, questions_url TEXT, scoring_url TEXT, data_json TEXT);
CREATE TABLE exam_items(id TEXT PRIMARY KEY, exam_set_id TEXT REFERENCES exam_sets(id), question_number INTEGER, data_json TEXT);
CREATE TABLE archive_audit(year INTEGER, resource_kind TEXT, data_json TEXT, PRIMARY KEY(year,resource_kind));
CREATE TABLE sources(id TEXT PRIMARY KEY, url TEXT, data_json TEXT);
CREATE TABLE metadata(key TEXT PRIMARY KEY, value_json TEXT);
CREATE INDEX question_topic ON questions(topic_id);
CREATE INDEX question_family ON questions(family_id);
CREATE VIEW student_questions AS SELECT id,topic_id,family_id,prompt FROM questions;
''')
for u in data['units']: db.execute('INSERT INTO units VALUES(?,?,?,?,?)',(u['id'],u['title'],u['mcq_min_pct'],u['mcq_max_pct'],json.dumps(u['recommended_prerequisite_units'])))
for t in topics: db.execute('INSERT INTO topics VALUES(?,?,?,?)',(t['id'],t['unit_id'],t['label'],json.dumps(t)))
for q in questions: db.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?)',(q['id'],q['topic_id'],q['family_id'],q['prompt'],q['origin'],q['review_status'],json.dumps(q)))
for s in solutions: db.execute('INSERT INTO solutions VALUES(?,?)',(s['question_id'],json.dumps(s)))
for h in hints: db.execute('INSERT INTO hints VALUES(?,?,?)',(h['question_id'],h['level'],h['text']))
for e in exam_sets: db.execute('INSERT INTO exam_sets VALUES(?,?,?,?,?)',(e['id'],e['year'],e['questions_url'],e['scoring_url'],json.dumps(e)))
for e in exam_items: db.execute('INSERT INTO exam_items VALUES(?,?,?,?)',(e['id'],e['exam_set_id'],e['question_number'],json.dumps(e)))
for e in archive_audit: db.execute('INSERT INTO archive_audit VALUES(?,?,?)',(e['year'],e['resource_kind'],json.dumps(e)))
for e in sources: db.execute('INSERT INTO sources VALUES(?,?,?)',(e['id'],e['url'],json.dumps(e)))
for k,v in metadata.items(): db.execute('INSERT INTO metadata VALUES(?,?)',(k,json.dumps(v)))
db.commit()
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not db.execute('PRAGMA foreign_key_check').fetchall()
db.close()

summary=dict(topics=len(topics),original_questions=len(questions),conceptual_questions=91,lab_data_representation_questions=8,numeric_questions=len(checks),
             numeric_families=26,numeric_variants_per_family="25 except formal_charge: 3 distinct cases",hints=len(hints),official_exam_sets=len(exam_sets),
             official_item_references=len(exam_items),copied_official_prompts=0,original_official_exam_solutions=0,
             per_unit_question_counts=dict(collections.Counter(int(q['topic_id'].split('.')[0]) for q in questions)),
             algebra_checks_passed=len(checks),expert_reviewed_items=0,sqlite_integrity='ok')
(ROOT/'validation_report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
