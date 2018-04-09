import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys


class Output():
    """General and study-specific .csv and chart outputs for en model """

    def __init__(self,
                 project,
                 study_name,
                 base_path = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3'
                 ):
        """sets up paths and loads input & output data"""

        # NB `data` is the results file, `study_scenarios' is the study parameters
        self.base_path =  base_path
        self.study_name = study_name
        self.project_path = os.path.join(self.base_path, project)
        self.input_path = os.path.join(self.project_path, 'inputs')
        # study file contains all scenarios (input parameters)
        self.study_filename = 'study_' + study_name + '.csv'
        self.studyFile = os.path.join(self.input_path, self.study_filename)
        # output folder contains result data
        self.output_path = os.path.join(self.project_path, 'outputs',self.study_name)
        self.scenario_path = os.path.join(self.output_path, 'scenarios')
        # plots
        self.plot_path = os.path.join(self.output_path,'plots')
        if not os.path.exists(self.plot_path):
                os.makedirs(self.plot_path)
        # read study scenarios
        self.study_scenarios = pd.read_csv(self.studyFile)
        self.study_scenarios.set_index('scenario', inplace=True)
        self.scenario_list = self.study_scenarios.index
        # Read list of output requirements and strip from self.df
        if 'output_types' in self.study_scenarios.columns:
            self.output_list = self.study_scenarios['output_types'].dropna().tolist()
        # read results file
        resultsFile = os.path.join(self.output_path,self.study_name+'_results.csv')
        self.data = pd.read_csv(resultsFile)
        self.data= self.data.set_index('scenario')

    def CsvOutput(self):
        """Format summary data from en model for csv output"""

        # Dict with required fields for summary table for different output_types
        # Fields can be from results csv or input parameters from study_...csv file
        # NB 'scenario' (integer) is index and included in csv by default
        summary_fields = {'csv_total_vs_type':
                             ['scenario_label','load_folder', 'arrangement', 'number_of_households',\
                              'total$_building_costs_mean','cp_ratio_mean','pv_ratio_mean'],
                          'csv_total_vs_tariff':
                              [ 'scenario_label','load_folder', 'arrangement', 'number_of_households',\
                              'total$_building_costs_mean','self-consumption_mean','pv_ratio_mean'],
                          'csv_another_one':
                              ['list', 'of','fields']
                          }
        for type in self.output_list:
            if 'csv_' in type:
                # add in fields from input parameters ('study_ .csv)
                for field in summary_fields[type]:
                    if field not in self.data.columns:
                        if field not in self.study_scenarios.columns:
                            sys.exit ('Field '+ field + ' not available')
                        else:
                            self.data.join(self.study_scenarios[field])
                # saves summary csv file
                summary = self.data.loc[:,summary_fields[type]]
                summaryFile = os.path.join(self.output_path,type[4:] + '.csv')
                summary.to_csv(summaryFile)
                print('Summary file '+type+ ' saved to '+ summaryFile)

    def plotOutput(self,type):
        """Plots single output chart(s)."""
        # NB These are very project-specific and need adaptation
        # put here for use as templates

        if type == 'bar_total_vs_site_arrangement':
            # -----------------------------
            # Barchart used for APSRC paper
            # -----------------------------
            # Barchart of total annual costs for different sites
            # (includes en and pv capex opex costs)
            # under different pv arrangements
            # 2 plots:  1 compares EN with btm, other compares btm scenarios

            self.df = self.data.copy()
            # ---------------
            # get site labels
            # ---------------
            self.df.loc[:,'site'] = self.df.loc[:,'load_folder'].apply(lambda x : x[-1])
            self.df.loc[:, 'labels'] = self.df.loc[:,'site']
            sites = self.df.loc[:, 'site'].drop_duplicates().tolist()
            sites=['A','E','D','B','H','I','G','C','J','F']
            floors = {'A':12,'E':7, 'D':9,'B':8,'H':3,'I':4,'G':44,'C':34,'J':26,'F':5}
            # floors = {s:floors[s] for s in sites}
            labels ={}
            for s, f in floors.items():
                u = (self.df.loc[self.df.loc[:,'site']==s,'number_of_households'].values[0]).astype(int)
                labels[s] = s +'('+str(u)+'/'+str(f)+')'

            print(labels)
            self.df.loc[:, 'label'] = self.df.loc[:, 'site'].apply(lambda x: labels[x])
            # ---------------------------------
            # calc total network energy per unit
            # ----------------------------------
            self.df['total$_building_costs_per_unit'] = self.df['total$_building_costs_mean']/ self.df['number_of_households']

            # Get rid of duplicates - assumed irrelevant as only variation is internal tariffs
            self.df['combined'] = self.df['site'] + self.df['arrangement']
            self.df = self.df.drop_duplicates('combined')
            self.df = self.df.drop('combined', axis=1)
            # ----------------------
            # reindex and stack data
            # ----------------------
            self.df.index = [self.df.label,self.df.arrangement]
            self.df = self.df['total$_building_costs_per_unit'].unstack()

            # --------------------------
            # Choose order of categories
            # --------------------------
            self.df = self.df.loc[[labels[s] for s in sites],:]

            # -----------------------------
            # Plot 2 different combinations
            # -----------------------------
            for i, arr_list in enumerate([['cp_only','bau', 'btm_icp', 'en', 'en_pv'], \
                                          ['bau', 'btm_icp', 'btm_s_c']]):
                ax = self.df[[c for c in self.df.columns if c in arr_list]].plot(kind='bar',figsize=(15, 10), fontsize=20)
                ax.set_xlabel("Site (Number units / number floors)", fontsize=20)
                ax.set_ylabel("Total Site Costs $ / unit", fontsize=20)
                ax.set_title ("Site Costs $ / Unit",fontsize=24)
                ax.legend(fontsize=20)
                ax.grid(True)
                plt.show()
                plotFile = os.path.join(self.plot_path,type + '_'+ '%02d' % i + '.png')
                plt.savefig(plotFile,dpi=1000)
                plt.close()

        if type == 'bar_en_income_vs_tariff':
            # ---------------------------------
            # barchart used for EnergyCON paper
            # ---------------------------------
            # This is bar chart showing $ benefit (Per annum) to strata of having an EN
            # Parameter is EN income (after PV cap payments but before EN capex and opex)
            # PLUS avoided cp energy charges
            # normalised for number of units
            # for different PV and amortization scenarios

            self.df = self.data.copy()

            # Get parent tariff and slice for 11.5c only
            self.df = self.df.join(self.study_scenarios['parent'])
            self.df['parent'] = self.df['parent'].fillna('N/A')
            self.df = self.df[self.df['parent'].str.contains('11.5c')]
            # Also, lose bau and cp_only
            self.df = self.df[~self.df['arrangement'].isin(['bau','cp_only'])]

            # -------------------------------
            #  Calc net ENO income $ per unit.
            # -------------------------------
            # en income - elec cost - pv_capex_repayments
            # doesn't include en capex repayments
            # (which are plotted seperately as threshold values)
            # !!!! Add in avoided common property charges
            self.df['en$_per_unit'] = (self.df['eno$_receipts_from_residents_mean']- \
                                       self.df['eno$_energy_bill_mean'] - self.df['pv_capex_repayment'] + \
                                       +self.data.loc[[self.data['arrangement'] == 'bau'][0], 'cust_bill_cp_mean'].values[0] # !!!! Add in avoided common prselferty charges
                                       )/ self.df ['number_of_households']

            self.df['en$_per_unit'] = self.df['en$_per_unit']

            # -------------------------------------------------------
            # Set up axis categories based  PV size and years payback
            # -------------------------------------------------------
            self.df = self.df.join(self.study_scenarios['pv_filename'])
            self.df = self.df.join(self.study_scenarios['all_residents'])
            def name_pv(x):
                if 'max' in x:
                    y = 'max PV'
                elif 'reduced' in x:
                    y = 'reduced PV'
                else:
                    y = 'no PV'
                return y
            self.df['pv'] = self.df['pv_filename'].fillna('none').apply(lambda x: name_pv(x))
            self.df = self.df.join(self.study_scenarios['a_term'])
            self.df['label'] = self.df['pv'] + self.df['a_term'].map(str)

            # ----------------------------------------------------------
            # TODO: iterate for different en_capex and opex scenarios
            # TODO: Calc en payback for each scenario and plot threshold
            # ---------------------------------------------------------

            # reindex and stack data
            # ----------------------
            self.df.index = [self.df.all_residents,self.df.label]
            self.df = self.df['en$_per_unit'].unstack()

            # --------------------------
            # Choose order of categories
            # --------------------------
            self.df = self.df[['max PV8.0','max PV12.0',  'reduced PV8.0', 'reduced PV12.0','no PVnan']]

            # plot barchart
            # -------------
            ax = self.df.plot(kind='bar',figsize=(15, 10), fontsize=20)
            ax.set_xlabel("Site", fontsize=20)
            ax.set_ylabel("ENO income $ / unit", fontsize=20)
            ax.set_title ("Embedded Network Income $ / Unit",fontsize=24)
            ax.legend(fontsize=20)
            ax.grid(True)

            # plot en capex thresholds
            # ------------------------

            plt.show()
            plotFile = os.path.join(self.plot_path,type  + '.png')
            plt.savefig(plotFile,dpi=1000)

        if type == 'scat_cust_sav_vs_sc_per_tariff':
            print('hi')
            # -----------------------------------------------------------
            # Scatter plot of customer savings vs self consumption metric
            # -----------------------------------------------------------
            # Each plot is for particular EN internal tariff,
            # for e.g. single site but multiple VBs
            # (but could be multiple sites?
            # compared to bau scenario (e.g TOU-15%)
            # colour-coded by total customer load
            # As used in EnergyCON paper)
            # uses self-consumption metric calculated independently
            self.df = self.data.copy()

            # Select EN scenarios with different EN tariffs , plus bau, or for different sites
            # --------------------------------------------------------------------------------
            self.study_scenarios['label'] = self.study_scenarios['site'].apply(lambda x: 'Site ' + x + ' ') + \
                                          self.study_scenarios['all_residents']
            self.study_scenarios[self.study_scenarios['arrangement'].isin(['en', 'en_pv', 'bau'])]
            self.df = self.df[self.df.index.isin(self.study_scenarios[self.study_scenarios['arrangement']
                                           .isin(['en', 'en_pv', 'bau'])].drop_duplicates('label').index)]
            self.df = self.df.join(self.study_scenarios['label'])

            # get bau data
            # ------------
            bau_scenario = self.df.loc[self.df['arrangement'].str.contains('bau'), 'scenario_label'].values[0]
            bau_path = os.path.join(self.scenario_path,bau_scenario+'.csv')
            d_bau = pd.read_csv(bau_path,index_col=[0])
            # slice for total customer costs
            total_cols = [c for c in d_bau.columns if 'cust_total$' in c and 'cp' not in c]
            num_units = len(total_cols)
            cols = [c for c in range(0, num_units)]
            drop_cols = [c for c in d_bau.columns if not c in total_cols]
            d_bau = d_bau.drop(drop_cols, axis=1)
            bau = d_bau.values.flatten()

            # Get lookup table to find customer numbers from vb
            # -------------------------------------------------
            vb_reference_path = 'C:\\Users\\z5044992\Documents\\MainDATA\\DATA_EN\\reference'
            vb_id = pd.read_csv(vb_reference_path + '\\vb_id_log.csv', index_col=0)
            sgsc_stats = pd.read_csv(vb_reference_path + '\\sgsc_self_consumption_metric.csv', index_col=0)

            # extract unit loads and sc metrics to plot against
            # -------------------------------------------------
            d_loads = pd.DataFrame(columns=cols)
            d_sc = pd.DataFrame(columns=cols)
            d_bau=d_bau
            cols = cols
            for row in d_bau.index.tolist():
                vb = row[-19:-4]
                d_loads.loc[vb,:] = sgsc_stats.loc[vb_id.loc[vb][0:num_units]].dropna()['kWh'].values
                d_sc.loc[vb,:] = sgsc_stats.loc[vb_id.loc[vb][0:num_units]].dropna()['sc_metric'].values
            kWh = d_loads.values.flatten()
            scm = d_sc.values.flatten()

            # iterate through tariff / site scenarios:
            # ----------------------------------------
            for label in [l for l in self.df.label if 'bau' not in l]:
                # get tariff data
                # ---------------
                tariff = self.study_scenarios.loc[
                    self.study_scenarios.label == label, 'all_residents'].drop_duplicates().values[0]
                tariff_scenario = self.df.loc[self.df['label'].str.contains(tariff), 'scenario_label'].values[0]
                tariff_path = os.path.join(self.scenario_path, tariff_scenario + '.csv')
                d_en = pd.read_csv(tariff_path,index_col=[0])
                d_en = d_en.drop(drop_cols, axis=1)
                en = d_en.values.flatten()

                # -------------
                # Scatter Plot
                # ------------
                plt.interactive(False)
                fig, ax = plt.subplots()
                title = 'Tariff: ' + label

                # Set up colour map
                # -----------------
                cmap = mpl.cm.Reds
                colours = []

                plot_name = label + '_%benefit_scm_kWh.png'
                plotFile = os.path.join(self.plot_path, plot_name)
                x_name = 'Self-consumption Metric %'
                y_name = 'Customer Saving (%)'
                x = scm
                y = (bau - en) / bau * 100
                l = y.tolist()
                pos = len([c for c in y.tolist() if c > 0]) / len(y.tolist()) * 100
                neg = len([c for c in y.tolist() if c < 0]) / len(y.tolist()) * 100

                x_max = 61
                alpha = 1
                print(label, 'pos = ', pos, '. neg = ', neg)

                for z in kWh.tolist():
                    colours = colours + [z]

                vmin = 0
                vmax = 10000
                # **************************************************************************************************

                y_max = 0
                y_min = 0
                scat = {}
                scat = ax.scatter(x, y, s=2, c=colours, cmap=cmap, vmin=vmin, vmax=vmax,alpha=alpha)  # edgecolors='k',
                x_max = max(x_max, max(x) * 1.1)
                x_min = 0
                y_min = min(y_min, min(y) * 1.1)
                y_max = max(y_max, max(y) * 1.1)
                fig.text(0.5, 0.02, x_name, ha='center', fontsize=16)
                fig.text(0.02, 0.5, y_name, va='center', rotation='vertical', fontsize=16)
                ax.set_xlim([x_min, x_max])
                ax.set_ylim([y_min, y_max])
                ax.grid(True)
                ax.set_title(title, fontsize=16, y=1.0)
                fig.savefig(plotFile, dpi=1000)
                plt.close()

        if type == 'scm_ssm_vs_pv':
            # ------------------------------------------------------
            # Plot of  self consumption and self-sufficiency metrics
            # ------------------------------------------------------
            # plots vs kWp and kWp per unit
            # Set up specifically for sgsc virtual buildings, sites A to J
            df = self.data.copy() # results
            df_in = self.study_scenarios.copy() # input parameters

            sites = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            dict_sites = dict(zip(sites, values))
            for s in df.index:
                df.loc[s,'s'] = df_in.loc[s,'load_folder'][-1]
                df.loc[s,'kWp'] = df_in.loc[s,'pv_kW_peak']
                df.loc[s,'kWp/unit'] = df.loc[s,'kWp'] / df.loc[s,'number_of_households']
                df.loc[s,'colour'] = dict_sites[df.loc[s,'s']]
            # df = df.drop([ 'arrangement', 'number_of_households',
            #        'load_folder', 'en_opex', 'en_capex_repayment', 'pv_capex_repayment',
            #        'average_hh_bill$', 'average_hh_total$', 'NUOS_charges$_mean',
            #        'cp_ratio_mean', 'cust_bill_cp_mean', 'cust_total$_cp_mean',
            #        'eno$_energy_bill_mean', 'eno$_receipts_from_residents_mean',
            #        'eno$_total_payment_mean', 'eno_net$_mean',
            #          'retailer_receipt$_mean',
            #         'total$_building_costs_mean'
            #        ], axis=1)

            # Plot self consumption metric  vs PV kW peak
            # -------------------------------------------
            cmap = mpl.cm.tab10
            fig, ax = plt.subplots()
            cmap = mpl.cm.tab10
            s = ax.scatter(df['kWp'], df['self-consumption_mean'], cmap=cmap, c=df['colour'], s=5, label=df['s'])
            cb = plt.colorbar(s)
            cb.set_label('site')
            cb.set_ticks(([s.colorbar.vmin + t * (s.colorbar.vmax - s.colorbar.vmin) for t in cb.ax.get_yticks()]))
            cb.set_ticklabels(sites)
            ax.set_xlabel("PV System kWp", fontsize=14)
            ax.set_ylabel("Self-Consumption % ", fontsize=14)
            ax.grid(True)
            ax.set_xlim([0,220])
            ax.set_ylim([0,110])
            plot_name = 'SelfConsumption_v_pv.png'
            plotFile = os.path.join(self.plot_path, plot_name)
            plt.savefig(plotFile, dpi=1000)

            # Plot self consumption metric  vs PV per unit
            # --------------------------------------------
            fig, ax = plt.subplots()
            cmap = mpl.cm.tab10
            s = ax.scatter(df['kWp/unit'], df['self-consumption_mean'], cmap=cmap, c=df['colour'], s=5, label=df['s'])
            cb = plt.colorbar(s)
            cb.set_label('site')
            cb.set_ticks(([s.colorbar.vmin + t * (s.colorbar.vmax - s.colorbar.vmin) for t in cb.ax.get_yticks()]))
            cb.set_ticklabels(sites)
            ax.set_xlabel("PV kWp per unit", fontsize=14)
            ax.set_ylabel("Self-Consumption % ", fontsize=14)
            ax.grid(True)
            ax.set_xlim([0,10])
            ax.set_ylim([0,110])
            plot_name = 'SelfConsumption_v_p_perUnit.png'
            plotFile = os.path.join(self.plot_path, plot_name)
            plt.savefig(plotFile, dpi=1000)

            # Calculate Self-Sufficiency (if required)
            # ----------------------------------------
            if not 'self-sufficiency_mean' in df.columns:
                for i in df.index:
                    df.loc[i, 'self-sufficiency_mean'] = (df.loc[i, 'total_building_load_mean']
                                                          - df.loc[i, 'import_kWh_mean']) / df.loc[
                                                             i, 'total_building_load_mean'] * 100



            # Plot self sufficiency metric  vs PV kW peak
            # -------------------------------------------
            cmap = mpl.cm.tab10
            fig, ax = plt.subplots()
            cmap = mpl.cm.tab10
            s = ax.scatter(df['kWp'], df['self-sufficiency_mean'], cmap=cmap, c=df['colour'], s=5, label=df['s'])
            cb = plt.colorbar(s)
            cb.set_label('site')
            cb.set_ticks(([s.colorbar.vmin + t * (s.colorbar.vmax - s.colorbar.vmin) for t in cb.ax.get_yticks()]))
            cb.set_ticklabels(sites)
            ax.set_xlabel("PV System kWp", fontsize=14)
            ax.set_ylabel("Self-Sufficiency % ", fontsize=14)
            ax.grid(True)
            ax.set_xlim([0,220])
            ax.set_ylim([0,50])
            plot_name = 'Selfsufficiency_v_pv.png'
            plotFile = os.path.join(self.plot_path, plot_name)
            plt.savefig(plotFile, dpi=1000)

            # Plot self sufficiency metric  vs PV per unit
            # --------------------------------------------
            fig, ax = plt.subplots()
            cmap = mpl.cm.tab10
            s = ax.scatter(df['kWp/unit'], df['self-sufficiency_mean'], cmap=cmap, c=df['colour'], s=5, label=df['s'])
            cb = plt.colorbar(s)
            cb.set_label('site')
            cb.set_ticks(([s.colorbar.vmin + t * (s.colorbar.vmax - s.colorbar.vmin) for t in cb.ax.get_yticks()]))
            cb.set_ticklabels(sites)
            ax.set_xlabel("PV kWp per unit", fontsize=14)
            ax.set_ylabel("Self-Sufficiency % ", fontsize=14)
            ax.grid(True)
            ax.set_xlim([0,10])
            ax.set_ylim([0,50])
            plot_name = 'Selfsufficiency_v_pv_perUnit.png'
            plotFile = os.path.join(self.plot_path, plot_name)
            plt.savefig(plotFile, dpi=1000)

            # Plot scm vs ssm
            # ---------------
            fig, ax = plt.subplots()
            cmap = mpl.cm.tab10
            s = ax.scatter(df['self-consumption_mean'], df['self-sufficiency_mean'], cmap=cmap, c=df['colour'], s=5, label=df['s'])
            cb = plt.colorbar(s)
            cb.set_label('site')
            cb.set_ticks(([s.colorbar.vmin + t * (s.colorbar.vmax - s.colorbar.vmin) for t in cb.ax.get_yticks()]))
            cb.set_ticklabels(sites)
            ax.set_xlabel("self Consumption", fontsize=14)
            ax.set_ylabel("Self-Sufficiency % ", fontsize=14)
            ax.grid(True)
            ax.set_xlim([0, 110])
            ax.set_ylim([0, 50])
            plot_name = 'ssm_scm.png'
            plotFile = os.path.join(self.plot_path, plot_name)
            plt.savefig(plotFile, dpi=1000)



    def plotAllOutputs(self):
        """Plot all required charts from en model results"""
        for type in self.output_list:
            print(type)
            self.plotOutput(type)
