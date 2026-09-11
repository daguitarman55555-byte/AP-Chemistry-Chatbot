"""Original teaching content, not exam solutions; expert review remains pending."""
CARDS=[
('1.1','Molar mass and particle counting','How do I convert mass into particles?',
 'Convert mass to amount using n=m/M, then multiply amount by the Avogadro constant. Track g, g/mol, mol, and particles explicitly.',
 'Equal masses of different substances need not contain equal particle counts.',
 'Which conversion factor cancels grams?', 'After obtaining moles, what factor connects moles and particles?'),
('2.1','Bond polarity versus molecular polarity','How do bond dipoles determine molecular polarity?',
 'Electronegativity differences produce bond dipoles. Molecular polarity depends on the vector sum of all dipoles and the molecular geometry; polar bonds can cancel in a symmetric arrangement.',
 'A molecule with polar bonds is not necessarily polar overall.',
 'What is the molecular geometry?', 'Do the bond dipole vectors cancel in that geometry?'),
('3.1','Intermolecular attractions and boiling','How do intermolecular forces affect boiling?',
 'Boiling separates molecules against intermolecular attractions; it does not usually break their covalent bonds. Compare hydrogen bonding, dipole interactions, polarizability, and molecular shape. All molecules exhibit London dispersion.',
 'Hydrogen bonding is not the only attraction present when molecules can hydrogen bond.',
 'Which attractions can operate between these particles?', 'How do particle size and contact area affect dispersion?'),
('4.1','Limiting reagent reasoning','How do I identify a limiting reactant?',
 'For a specified complete reaction, first balance the equation. Convert available amounts to moles and divide each by its stoichiometric coefficient. The smallest ratio limits the possible reaction extent.',
 'The reactant with the least mass is not necessarily limiting.',
 'Have you converted both reactant amounts to moles?', 'How much reaction extent does each coefficient permit?'),
('5.1','Rate laws from experimental data','How do I determine reaction orders from initial rates?',
 'Compare experiments where one reactant concentration changes while the others remain fixed. Relate the rate ratio to the concentration ratio raised to an unknown order. Overall balanced coefficients do not generally determine the experimental rate law.',
 'Stoichiometric coefficients can be used as rate-law exponents only for a specified elementary step, not an arbitrary overall reaction.',
 'Which pair of trials holds the other concentrations constant?', 'What exponent relates the concentration ratio to the rate ratio?'),
('6.1','Calorimetry system and surroundings','How do I choose the sign of calorimetry heat?',
 'Define the system before choosing a sign. A warming solution absorbs heat. In an ideal isolated calorimeter, reaction heat is the negative of heat absorbed by the solution and calorimeter. The expression q=mc delta T requires an appropriate heat capacity and no unaccounted phase change.',
 'A temperature increase in the surroundings does not mean positive reaction heat.',
 'Are you calculating heat for the reaction or for the solution?', 'Where did the energy that warmed the solution come from?'),
('7.1','Reaction quotient and equilibrium','How do Q and K predict reaction direction?',
 'Construct Q using the same reaction and expression as K. At the stated temperature, Q below K favors net forward reaction; Q above K favors net reverse reaction. At equilibrium the forward and reverse rates are equal, not necessarily the concentrations.',
 'Equilibrium does not require equal reactant and product concentrations.',
 'Are Q and K written for the same balanced reaction?', 'Which net direction would bring the quotient toward K?'),
('8.1','Acid strength versus concentration','What is the difference between acid strength and concentration?',
 'Acid strength describes the extent of proton transfer to water and is characterized by Ka at a given temperature. Concentration describes the amount of solute per volume. A weak acid can be concentrated, and a strong acid can be dilute.',
 'Weak acid does not mean dilute acid.',
 'Does the statement describe how much acid is present or how extensively it ionizes?', 'Which information would you need to compare the hydrogen ion concentrations?'),
('9.1','Thermodynamic favorability and speed','Does a favorable reaction have to be fast?',
 'Negative Gibbs energy change indicates thermodynamic favorability for the stated conditions. Reaction speed depends on kinetics and activation barriers. A catalyst changes the reaction pathway and rates but does not change the equilibrium constant or standard Gibbs energy change.',
 'Thermodynamically favorable does not mean instantaneous.',
 'Is the question about equilibrium direction or reaction speed?', 'Would changing an activation barrier alter the initial and final thermodynamic states?'),
]

def teaching_chunks(topics):
    chunks=[]
    for index,(topic,title,question,text,misconception,hint1,hint2) in enumerate(CARDS):
        chunks.append(dict(id=f'teaching-{index+1}',topic_id=topic,title=title,question=question,
            text=text+' Misconception to address: '+misconception,
            guiding_questions=[hint1,hint2],review_status='authored_not_expert_reviewed',
            source_url=topics[topic]['source_url'],source_role='curriculum_alignment_not_verbatim_source'))
    return chunks
