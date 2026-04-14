import questionary # for pretty command-line selections
import pandas # for collecting data
import ComplexityCollector
import FactorAnalysis
import LatexExporter
from modelcomplexity import ModelComplexityMeasures
from discovery import DiscoveryAlgorithms

def print_welcome_message():
    print("Welcome to ComFy: a tool to perform a factor analysis on complexity measures for Petri nets!")

def ask_user_for_complexity_measures(question: str):
    # collect all possible complexity measures.
    measures = [questionary.Choice(title=str(measure), value=measure) for measure in ModelComplexityMeasures.all_model_complexity_measures]
    # ask the user to choose a subset of these complexity measures.
    model_measures = questionary.checkbox(question, choices=measures).ask()
    return model_measures

def ask_user_for_discovery_algorithms(question: str):
    # collect all possible discovery algorithms.
    miners = [questionary.Choice(title=str(miner), value=miner) for miner in DiscoveryAlgorithms.analyzed_discovery_algorithms]
    # ask the user to choose a subset of these discovery algorithms.
    selected_miners = questionary.checkbox(question, choices=miners).ask()
    return selected_miners

def ask_user_if_they_want_to_proceed(question: str):
    response = questionary.select(question, choices=["yes","no"]).ask()
    return response

def ask_user_for_number(question: str):
    response = questionary.text(question).ask()
    while True:
        try:
            number = int(response)
            return number
        except ValueError:
            print("Invalid input: " + response + " cannot be converted to an integer.")
            print("Please try again.")

def ask_user_for_rotation(question: str):
    rotations = ['varimax', 'promax', 'oblimin', 'oblimax', 'quartimin', 'quartimax', 'equamax', 'no rotation']
    response = questionary.select(question, choices=rotations).ask()
    return response

if __name__ == "__main__":
    print_welcome_message()
    # collect the set of complexity measure the user wants to analyze.
    model_measures = ask_user_for_complexity_measures("Please select which complexity measures you wish to analyze.")
    # collect the discovery algorithms the user wants to use to compute Petri nets.
    selected_miners = ask_user_for_discovery_algorithms("Please select which discovery algorithms you wish to use to generate Petri nets.")
    # collect the complexity scores for the models found by the selected discovery algorithms.
    complexity, sample_size = ComplexityCollector.discover_and_collect_complexity_scores(selected_miners, model_measures)
    # create an instance of a class to perform the factor analysis.
    CFA = FactorAnalysis.ComplexityFactorAnalysis(complexity)
    # check if the data is fit for a factor analysis.
    CFA.clean_data_from_constant_variables()
    bartlett_ok = CFA.execute_Bartletts_test_of_sphericity()
    if not bartlett_ok:
        response = ask_user_if_they_want_to_proceed("Do you wish to proceed anyway?")
        if response == "no":
            print("Exiting program. Goodbye!")
            exit()
    msa_ok = CFA.repeat_calculate_measure_of_sampling_adequacy()
    if not msa_ok:
        print("I will exit the program, since a factor analysis might not be valid.")
        exit()
    # perform the factor analysis on the collected data.
    print("\nNow, let us perform the statistical analysis.")
    print("I will next ask you for the number of factors you expect.")
    show_scree_answer = ask_user_if_they_want_to_proceed("Do you want to see a Scree plot to make an informed decision on the number of factors?")
    show_scree_plot = False
    if show_scree_answer == "yes":
        show_scree_plot = True
    CFA.calculate_scree_plot(show_scree_plot)
    expected_factors = ask_user_for_number("Please enter the number of factors you expect.")
    rotation_answer = ask_user_for_rotation("Which rotation do you want to perform on the data?")
    rotation = None
    if rotation_answer != 'no rotation':
        rotation = rotation_answer
    print("\nI will now perform the factor analysis.")
    response = ask_user_if_they_want_to_proceed("Do you want the results to appear on the command line?")
    show_results = False
    if response == "yes":
        show_results = True
    CFA.perform_factor_analysis(expected_factors, rotation=rotation, show_plot=show_results)
    print("\nI will now export the results of the factor analysis to a LaTeX file.")
    latex_exporter = LatexExporter.LatexExporter(CFA, selected_miners, model_measures, sample_size)
    latex_exporter.export()
