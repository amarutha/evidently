#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import plotly.figure_factory as ff

from evidently.analyzers.num_target_drift_analyzer import NumTargetDriftAnalyzer
from evidently.model.widget import BaseWidgetInfo, AlertStats
from evidently.widgets.widget import Widget, GREY, RED


class NumOutputDriftWidget(Widget):
    def __init__(self, title: str, kind: str = 'target'):
        super().__init__(title)
        self.kind = kind #target or prediction

    def analyzers(self):
        return [NumTargetDriftAnalyzer]

    def get_info(self) -> BaseWidgetInfo:
        return self.wi

    def calculate(self,
                  reference_data: pd.DataFrame,
                  current_data: pd.DataFrame,
                  column_mapping,
                  analyzers_results):

        results = analyzers_results[NumTargetDriftAnalyzer]

        if results['utility_columns'][self.kind] is not None:
            #calculate output drift
            output_p_value = results['metrics'][self.kind + '_drift']
            output_sim_test = "detected" if output_p_value < 0.05 else "not detected"

            #plot output distributions
            output_distr = ff.create_distplot(
                [reference_data[results['utility_columns'][self.kind]],
                current_data[results['utility_columns'][self.kind]]],
                ["Reference", "Current"],
                colors=[GREY, RED],
                show_rug=True)

            output_distr.update_layout(
                xaxis_title = "Value",
                yaxis_title = "Share",
                legend = dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
                )
            )

            output_drift_json  = json.loads(output_distr.to_json())

            self.wi = BaseWidgetInfo(
                title=self.kind.title() + " drift: ".title() + output_sim_test + ", p_value=" + str(round(output_p_value, 6)),
                type="big_graph",
                details="",
                alertStats=AlertStats(),
                alerts=[],
                alertsPosition="row",
                insights=[],
                size=2,
                params={
                    "data": output_drift_json['data'],
                    "layout": output_drift_json['layout']
                },
                additionalGraphs=[],
            )
        else:
            self.wi = None
