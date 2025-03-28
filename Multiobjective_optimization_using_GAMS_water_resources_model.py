# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 17:16:41 2024

@author: Hector Macian-Sorribes
"""


## CALCULATION OF NATIVE HABITAT FROM SINGLE STREAMFLOW 
    
def native_habitat_calculus(streamflow):
    
    import pandas as pd

    fichero_habitat = pd.read_csv('C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\' + 'Habitat_and_competition.csv', sep = ';')
    
    if streamflow <= 5:
    
        new_streamflow = (np.round(streamflow*2, 1)) / 2
        
    else:
        
        new_streamflow = 5.0
    
    return fichero_habitat.loc[fichero_habitat['Qstream'].isin([new_streamflow])]['Habitat_natives'].values[0]


## CALCULATION OF COMPETITION FROM SINGLE STREAMFLOW 

def competition_calculus(streamflow):
    
    import pandas as pd

    fichero_habitat = pd.read_csv('C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\' + 'Habitat_and_competition.csv', sep = ';')
    
    if streamflow <= 5:
    
        new_streamflow = (np.round(streamflow*2, 1)) / 2
        
    else:
        
        new_streamflow = 5.0
    
    return fichero_habitat.loc[fichero_habitat['Qstream'].isin([new_streamflow])]['Competition'].values[0]


# Cambio de archivos .txt

def single_substitution(archivo_entrada, archivo_salida, month, zone, value):
    
    if month < 10:
    
        param_to_substitute = 'param0' + str(month) + str(zone)
        
    else:
        
        param_to_substitute = 'param' + str(month) + str(zone)

    sustituciones = {param_to_substitute: str(value)}
    
    # Leer el archivo de entrada
    
    with open(archivo_entrada, 'r', encoding='utf-8') as file:
        
        contenido = file.read()
    
    # Realizar las sustituciones
    
    for original, nuevo in sustituciones.items():
        
        contenido = contenido.replace(original, nuevo)
    
    # Crear el archivo de salida con el contenido modificado
    
    with open(archivo_salida, 'w', encoding='utf-8') as file:
        
        file.write(contenido)
        
def multiple_substitutions(archivo_entrada, archivo_salida, month_values, zone_values, values):
    
    for value in range(len(month_values)):
            
        if value == 0:
            
            single_substitution(archivo_entrada, archivo_salida, month_values[value], zone_values[value], np.round(values[value],4))
                       
        else:
            
            single_substitution(archivo_salida, archivo_salida, month_values[value], zone_values[value], np.round(values[value],4))
                  

##################
### CODE START ###
##################



import pandas as pd
import numpy as np
from platypus import Problem, Real, nondominated
from pyborg import BorgMOEA
import os


climate_models = ['GFDL_ESM4', 'IPSL_CM6A_LR', 'MPI_ESM1_2_HR', 'MRI_ESM2_0', 'UKESM1_0_11']
climate_scenarios = ['ssp126', 'ssp585']
landuse_scenarios = ['Actual', 'PHJ', 'Tend']
time_horizons = ['cp','mp']

niter = 2500
  
for climate in climate_scenarios:

    for landuse in landuse_scenarios:

        for horizon in time_horizons:
                
            for model in climate_models:
                
                filename = 'C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\Hola.csv'
                
                if os.path.isfile(filename) == True:
                    
                    pass
                
                else:

                    # Cambiar fichero sueltas
                    
                    archivo_entrada = 'C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\Zone_reservoir_releases_original.txt'
                    
                    ruta_ficheros = 'D:\\HECTOR\\GamSim\\SERPIS\\CALCULOS_PAPER_NCC\\2_ESCENARIOS\\' + model + '\\' + climate + '\\' + landuse + '_' + horizon + '\\'
                    
                    archivo_salida = ruta_ficheros + 'Zone_reservoir_releases.txt'
                    
                    # Actualizar el archivo .bat
                        
                    with open('D:\\Ejecuta_GAMS_Serpis_original.bat', 'r', encoding='utf-8') as file:
                        
                        contenido = file.read()
               
                    contenido = contenido.replace('texto_original', 'cd D:\\HECTOR\\GamSim\\SERPIS\\CALCULOS_PAPER_NCC\\2_ESCENARIOS\\' + model + '\\' + climate + '\\' + landuse + '_' + horizon + '\\')
                    
                    # Crear el archivo de salida con el contenido modificado
                    
                    with open('D:\\Ejecuta_GAMS_Serpis.bat', 'w', encoding='utf-8') as file:
                        
                        file.write(contenido)
                    
                    def problema_Serpis(values):
                        
                        import subprocess
                    
                        month_values = [1,1,1,1,
                                        2,2,2,2,
                                        3,3,3,3,
                                        4,4,4,4,
                                        5,5,5,5,
                                        6,6,6,6,
                                        7,7,7,7,
                                        8,8,8,8,
                                        9,9,9,9,
                                        10,10,10,10,
                                        11,11,11,11,
                                        12,12,12,12]
                        
                        zone_values = [1,2,3,4] * 12
                        
                        multiple_substitutions(archivo_entrada, archivo_salida, month_values, zone_values, values)
                        
                        # Ejecutar GAMS                
                        
                        subprocess.run([r'D:\\Ejecuta_GAMS_Serpis.bat'])
                        
                        # Recuperar resultados
                        
                        import pandas as pd                
                        
                        max_benefits = pd.read_csv('C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\Beneficios_maximos_demandas.csv', sep = ';') 
                        
                        maximum_benefits = max_benefits.loc[(max_benefits['Modelo'] == model) & (max_benefits['Uso_suelo'] == landuse) & (max_benefits['Clima'] == climate) & (max_benefits['Plazo'] == horizon)  ]
                        
                        max_Ben_CA = maximum_benefits['Ben_CA'].values[0]
                        max_Ben_CB = maximum_benefits['Ben_CB'].values[0]
                                                            
                        Excel_caudales = pd.read_excel(ruta_ficheros + 'stig_Stream_habitat.xlsx', header = None)
                        Excel_beneficios = pd.read_excel(ruta_ficheros + 'stig_Benefits_BORG.xlsx', header = None)
                        
                        output_dataframe_caudales = pd.DataFrame(index = Excel_caudales.index)
                        output_dataframe_beneficios = pd.DataFrame(index = Excel_beneficios.index)  
                    
                        years = Excel_beneficios.iloc[:,0].values
                        months = Excel_beneficios.iloc[:,1].values
                        
                        for year in range(len(years)):
                                                
                            years[year] = years[year][9:]
                            months[year] = months[year][1:]
                              
                        output_dataframe_caudales['Year'] = years
                        output_dataframe_caudales['Month'] = months
                        
                        output_dataframe_beneficios['Year'] = years
                        output_dataframe_beneficios['Month'] = months
                        
                        output_dataframe_caudales['Caudal'] = Excel_caudales.iloc[:,-1].values
                        caudales_tramo = output_dataframe_caudales['Caudal'].values
                        
                        habitats = [native_habitat_calculus(x) for x in caudales_tramo]
                        competitions = [competition_calculus(x) for x in caudales_tramo]
                        
                        output_dataframe_caudales['Habitat'] = habitats
                        output_dataframe_caudales['Competition'] = competitions
                                           
                        output_dataframe_beneficios['Beneficios'] = Excel_beneficios.iloc[:,-1].values / (max_Ben_CA + max_Ben_CB) * (10.36 + 8.33)
                        
                        output_dataframe_yearly_habitat = output_dataframe_caudales.groupby(['Year']).min()
                        
                        output_dataframe_yearly_competition = output_dataframe_caudales.groupby(['Year']).max()
                        
                        output_dataframe_yearly_benefits = output_dataframe_beneficios.groupby(['Year']).sum()
                        
                        caudales_tramo = output_dataframe_caudales['Caudal'].values
                        
                        habitats = [native_habitat_calculus(x) for x in caudales_tramo]
                        competitions = [competition_calculus(x) for x in caudales_tramo]
                        
                        output_dataframe_caudales['Habitat'] = habitats
                        output_dataframe_caudales['Competition'] = competitions
                        
                        annual_benefits_total = output_dataframe_yearly_benefits['Beneficios'].values
                        
                        benefit_metric = - np.mean(annual_benefits_total)
                        
                        annual_habitat = output_dataframe_yearly_habitat['Habitat'].values
                        annual_competition = output_dataframe_yearly_competition['Competition'].values
                        
                        habitat_metric = - np.mean(annual_habitat)
                        competition_metric = np.mean(annual_competition)
                    
                        return benefit_metric, habitat_metric, competition_metric
                    
                    problem = Problem(48, 3)
                    
                    problem.types[:] = Real(0, 20)
                    
                    problem.function = problema_Serpis
                    problem.directions[0] = Problem.MINIMIZE
                    problem.directions[1] = Problem.MINIMIZE
                    problem.directions[2] = Problem.MINIMIZE
                    
                    algorithm = BorgMOEA(problem, epsilons = 0.1)
                    algorithm.run(niter)
                    
                    # Obtener objetivos
                    
                    nondominated_solutions = nondominated(algorithm.result)
                    
                    Benefit_points = [ - s.objectives[0] for s in nondominated_solutions]
                    Habitat_points = [ - s.objectives[1] for s in nondominated_solutions]
                    Competition_points = [s.objectives[2] for s in nondominated_solutions]
                    
                    # Obtener variables
                    
                    solution_number = list(range(len(Benefit_points)))
                    
                    auxiliar_dataframe_solutions = pd.DataFrame(index = list(range(48)))
                    
                    month_values = [1,1,1,1,
                                    2,2,2,2,
                                    3,3,3,3,
                                    4,4,4,4,
                                    5,5,5,5,
                                    6,6,6,6,
                                    7,7,7,7,
                                    8,8,8,8,
                                    9,9,9,9,
                                    10,10,10,10,
                                    11,11,11,11,
                                    12,12,12,12]
                    
                    zone_values = [1,2,3,4] * 12
                    
                    auxiliar_dataframe_solutions['Month'] = month_values
                    auxiliar_dataframe_solutions['Zone'] = zone_values
                    
                    for sol_num in range(len(Benefit_points)):
                        
                        name_column_sol = 'sol' + str(sol_num + 1)
                        auxiliar_dataframe_solutions[name_column_sol] = nondominated_solutions[sol_num].variables[:]
                    
                    output_dataframe_solutions = auxiliar_dataframe_solutions.copy()
                    
                    output_dataframe_objectives = pd.DataFrame(index = solution_number)
                    
                    output_dataframe_objectives['Benefits'] = Benefit_points
                    output_dataframe_objectives['Habitat'] = Habitat_points
                    output_dataframe_objectives['Competition'] = Competition_points
                    
                    #output_dataframe_solutions.to_csv('C:\\Users\\hecmasor\\OneDrive - UPV\\INVESTIGACION\\PAPERS\\8_Serpis_Biodiversidad\\3_PAPER_2\\' + 'Optimal_solutions_Serpis_Actual_BORGMOEA_' + str(niter) + '_iter.csv', sep=';')
                    #output_dataframe_objectives.to_csv('C:\\Users\\hecmasor\\OneDrive - UPV\\INVESTIGACION\\PAPERS\\8_Serpis_Biodiversidad\\3_PAPER_2\\' + 'Pareto_front_Serpis_Actual_BORGMOEA_' + str(niter) + '_iter.csv', sep=';')
                    
                    output_dataframe_solutions.to_csv('C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\' + 'Optimal_solutions_Serpis_' + model + '_' + climate + '_' + landuse + '_' + horizon + '_BORGMOEA_' + str(niter) + '_iter.csv', sep=';')
                    output_dataframe_objectives.to_csv('C:\\Users\\hecmasor\\PAPERS\\Serpis_NCC\\' + 'Pareto_front_Serpis_' + model + '_' + climate + '_' + landuse + '_' + horizon + '_BORGMOEA_' + str(niter) + '_iter.csv', sep=';')
                    
    
