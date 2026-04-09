import pandas # for collecting data
import Constants
import numpy as np

class LatexExporter():
    def __init__(self, complexityFactorAnalysis, selected_miners, selected_measures, sample_size):
        self.CFA = complexityFactorAnalysis
        self.miners = selected_miners
        self.measures = selected_measures
        self.sample_size = sample_size

    def start_latex_report(self):
        f = open(Constants.LATEX_REPORT_PATH, "w")
        f.write("\\documentclass[a4paper]{article}\n\n")
        f.write("\\usepackage[margin=1in]{geometry}\n")
        f.write("\\usepackage{graphicx}\n")
        f.write("\\usepackage{booktabs}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usepackage{pgfplots}\n")
        f.write("\\usepackage{paralist}\n")
        f.write("\\pgfplotsset{compat=1.16}\n\n")
        f.write("\\begin{document}\n\n")
        f.write("\\section*{Chosen Discovery Algorithms}\n")
        f.write("For this factor analysis, you chose the following miners to discover process models:\n")
        f.write("\\begin{compactitem}\n")
        for miner in self.miners:
            f.write("\\item " + str(miner) + "\n")
        f.write("\\end{compactitem}\n\n")
        f.write("This means, for each input event log, the program discovered models using each of the aforementioned discovery algorithms.\n")
        f.write("For the resulting Petri nets, it calculated the complexity score of each selected measure, which formed the population.\n")
        f.write("\nYou chose to analyze the following complexity measures:\n")
        f.write("\\begin{compactitem}\n")
        for measure in self.measures:
            f.write("\\item " + str(measure) + "\n")
        f.write("\\end{compactitem}\n\n")
        f.close()

    def export_analysis_validity(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\section*{Validity of the Factor Analysis}\n")
        f.write("Your sample size in this analysis was $" + str(self.sample_size) + "$.\n")
        f.write("It is recommended to have a sample size of at least $5 \\cdot " + str(len(self.measures)) + " = " + str(5*len(self.measures)) + "$.\n\n")
        f.write("Bartlett's test of sphericity returned a $\\chi^2$ value of $" + str(self.CFA.bartlett_chi_squared) + "$ and a $p$-value of $" + str(self.CFA.bartlett_p_value) + "$.\n")
        if self.CFA.bartlett_p_value < Constants.bartlett_p_value_threshold:
            f.write("This means, the variables are probably correlated and we can perform a factor analysis.\n\n")
        else:
            f.write("This means, the variables are probably not correlated and performing a factor analysis is \\textbf{not} advised.\n\n")
        f.write("The measure of sampling adequacy (MSA) returned the following results:\n")
        f.write("\\begin{compactitem}\n")
        index = 0
        for measure in list(self.CFA.complexity_data):
            f.write("\\item " + str(measure) + ": $" + str(round(self.CFA.msa_per_variable[index], Constants.number_of_decimals)) + "$\n")
            index += 1
        f.write("\\item overall MSA: $" + str(self.CFA.overall_msa) + "$\n")
        f.write("\\end{compactitem}\n\n")
        if len(self.CFA.msa_insufficient_variables.keys()) > 0:
            f.write("\\noindent\nDuring the analysis, the MSA values of the following complexity measures were too low:\n")
            f.write("\\begin{compactitem}\n")
            for measure in self.CFA.msa_insufficient_variables.keys():
                f.write("\\item " + str(measure) + ": $" + str(round(self.CFA.msa_insufficient_variables[measure], Constants.number_of_decimals)) + "$\n")
            f.write("\\end{compactitem}\n")
            f.write("These complexity measures were left out of the analysis to produce dependable results.\n\n")
        f.close()

    def export_number_of_factors(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\section*{Chosen Number of Factors}\n")
        f.write("The Scree test resulted in the following Eigenvalue plot:\n")
        f.write("\\begin{center}\n")
        f.write("\\begin{tikzpicture}\n")
        f.write("\\begin{axis}[xtick=data,width=15cm,height=8cm]\n")
        f.write("\\addplot [draw=cyan!50!blue, mark=*] coordinates {")
        for index in range(len(self.CFA.pca_explained_variance_ratio)):
            f.write(" (" + str(index + 1) + "," + str(round(self.CFA.pca_explained_variance_ratio[index], Constants.number_of_decimals)) + ")")
        f.write("};\n")
        f.write("\\end{axis}\n")
        f.write("\\end{tikzpicture}\n")
        f.write("\\end{center}\n")
        f.write("You choose to set the number of expected factors to $" + str(self.CFA.number_of_factors) + "$.\n\n")
        f.close()

    def export_descriptive_statistics(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\section*{Descriptive Statistics}\n")
        f.write("\\begin{center}\n")
        f.write(self.CFA.descriptive_statistics.to_latex())
        f.write("\\end{center}\n\n")
        f.close()

    def export_factor_analysis_results(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\section*{Results of the Factor Analysis}\n")
        rows = len(self.CFA.factor_loadings)
        columns = len(self.CFA.factor_loadings[0])
        f.write("\\begin{center}\n")
        f.write("\\begin{tabular}{c")
        for i in range(columns):
            f.write("c")
        f.write("} \\toprule \n")
        for i in range(columns):
            f.write(" & Factor " + str(i+1))
        f.write(" \\\\ \\midrule \n")
        for i in range(rows):
            f.write(str(list(self.CFA.complexity_data)[i]))
            for j in range(columns):
                value = round(self.CFA.factor_loadings[i][j], Constants.number_of_decimals)
                if abs(value) < Constants.ignore_threshold:
                    f.write(" & \\textcolor{lightgray}{$" + str(value) + "$}")
                else:
                    f.write(" & $" + str(value) + "$")
            f.write(" \\\\ \n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{center}\n\n")
        f.close()

    def export_communalities(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\section*{Communalities}\n")
        f.write("\\begin{center}\n")
        f.write("\\begin{tikzpicture}\n")
        x_coords = ""
        for measure in list(self.CFA.complexity_data):
            x_coords += str(measure) + ","
        x_coords = x_coords[0:-1]
        f.write("\\begin{axis}[ybar,symbolic x coords={" + x_coords + "},xtick=data,xticklabel style={rotate=45, anchor=east},nodes near coords={\\pgfmathprintnumber{\\pgfplotspointmeta}},width=15cm,height=8cm]\n")
        f.write("\\addplot [draw=cyan!50!blue, fill=cyan!50!blue] plot coordinates {")
        complexity_names = [str(measure) for measure in list(self.CFA.complexity_data)]
        communalities = pandas.Series(self.CFA.communalities, index=list(self.CFA.complexity_data))
        index = 0
        for c in communalities:
            f.write(" (" + str(list(self.CFA.complexity_data)[index]) + "," + str(round(c, Constants.number_of_decimals)) + ")")
            index += 1
        f.write("};\n")
        f.write("\\end{axis}\n")
        f.write("\\end{tikzpicture}\n")
        f.write("\\end{center}\n\n")
        f.close()

    def end_latex_report(self):
        f = open(Constants.LATEX_REPORT_PATH, "a")
        f.write("\\end{document}\n")
        f.close()

    def export(self):
        self.start_latex_report()
        self.export_analysis_validity()
        self.export_number_of_factors()
        self.export_descriptive_statistics()
        self.export_factor_analysis_results()
        self.export_communalities()
        self.end_latex_report()
        print("A LaTeX report was exported to " + str(Constants.LATEX_REPORT_PATH) + ".")
