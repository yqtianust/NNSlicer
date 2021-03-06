import os, sys
import numpy as np
from pdb import set_trace as st
import pandas as pd

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import axes
import matplotlib.ticker as ticker

dir =  f"models/prune/f1_score/fc"
modes = [
    "posnegweight_small",
    # "posonly_small",
]

fig_dir = os.path.join(dir, "fig")
os.makedirs(fig_dir, exist_ok=True)
exp_configs = {
    "fc": ["dense"],
    "block4fc": ["conv2d_10", "conv2d_11", "conv2d_12", "dense"],
    # "conv12": ["conv2d_12"],
    # "block4": ["conv2d_10", "conv2d_11", "conv2d_12"],
    # "block4main": ["conv2d_11", "conv2d_12"],
}

def draw_posneg_weight_cmp_hist():
    for exp_name in exp_configs.keys():
        # All trace on each class
        filename = f"lastconv_{exp_name}_class_all.csv"
        path = os.path.join(dir, filename)
        all_df = pd.read_csv(path, index_col=0)
        
        for ratio in np.unique(all_df["ratio"]):
            df = all_df[all_df['ratio'] == round(ratio, 1)]
            posneg = df['posnegweight_small'].to_list()
            weight = df['edgeweight_small'].to_list()
            class_ids = df['test_class'].to_list()
            
            fig, ax = plt.subplots(figsize=(8,6))
            width = 0.4
            rects1 = plt.bar(left=class_ids, height=posneg, width=0.4, label="Trace")
            rects2 = plt.bar(left=[i + width for i in class_ids], height=weight, width=0.4, label="Weight")
            
            ax.set_ylabel("F1 Score")
            ax.set_xlabel("Test Class")
            ax.set_title("Pruned Performance")
            ax.set_xticks([p + 0.5 * width for p in class_ids])
            ax.set_xticklabels(class_ids)
            plt.ylim(0, 1)
            
            plt.legend()
            
            fig_name = f"posneg_weight_cmp_hist_{exp_name}_all_ratio{round(ratio,1)}.pdf"
            fig_path = os.path.join(fig_dir, fig_name)
            plt.savefig(fig_path)
            plt.clf()
        
        # Class trace on each class
        for ratio in np.unique(all_df["ratio"]):
            results = []
            for class_id in range(10):
                filename = f"lastconv_{exp_name}_class_{class_id}.csv"
                path = os.path.join(dir, filename)
                df = pd.read_csv(path, index_col=0) 
                df = df[df['ratio'] == round(ratio, 1)]
                df = df[df['test_class'] == class_id]
                results.append(df)
            class_df = pd.concat(results)
            
            posneg = class_df['posnegweight_small'].to_list()
            weight = class_df['edgeweight_small'].to_list()
            class_ids = class_df['test_class'].to_list()
            
            fig, ax = plt.subplots(figsize=(8,6))
            width = 0.4
            rects1 = plt.bar(left=class_ids, height=posneg, width=0.4, label="Trace")
            rects2 = plt.bar(left=[i + width for i in class_ids], height=weight, width=0.4, label="Weight")
            
            ax.set_ylabel("F1 Score")
            ax.set_xlabel("Test Class")
            ax.set_title("Pruned Performance")
            ax.set_xticks([p + 0.5 * width for p in class_ids])
            ax.set_xticklabels(class_ids)
            plt.ylim(0, 1)
            
            plt.legend()
            
            fig_name = f"posneg_weight_cmp_hist_{exp_name}_perclass_ratio{round(ratio,1)}.pdf"
            fig_path = os.path.join(fig_dir, fig_name)
            plt.savefig(fig_path)
            plt.clf()
    
    
def draw_heatmap_expconfig():
    for mode in modes:
        for exp_name in exp_configs.keys():
            for ratio in np.arange(0.1, 1.0, 0.1):
                print(f"{mode} {exp_name} ratio={ratio}")
                interclass_matrix = []
                for class_id in list(range(10)):
                    # filename = f"allconv_class_{exp_name}_{class_id}.csv"
                    filename = f"lastconv_{exp_name}_class_{class_id}.csv"
                    path = os.path.join(dir, filename)
                    df = pd.read_csv(path, index_col=0)
                    df = df[df['ratio'] == round(ratio, 2)]
                    df = df.sort_values(by="test_class", ascending=True)
                    
                    df = df[mode]
                    interclass_matrix.append(df.to_numpy())
                
                interclass_matrix = np.stack(interclass_matrix)
                print(interclass_matrix)
                print()
                
                # plot
                fig_name = f"{mode}_{exp_name}_ratio={round(ratio, 2)}.pdf"
                fig_path = os.path.join(fig_dir, fig_name)
                fig = plt.figure()
                ax = fig.add_subplot(111)
                cax = ax.matshow(
                    interclass_matrix, 
                    interpolation='nearest', cmap='winter',
                )
                fig.colorbar(cax)
                
                tick_spacing = 1
                ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
                ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
                
                ax.set_xticklabels([''] + list(range(10)))
                ax.set_yticklabels([''] + list(range(10)))
                ax.set_title(f"Relationship Between Trace Class and Test Class\n"
                            f"{exp_name} prune ratio {ratio}")
                
                for i in range(10):
                    for j in range(10):
                        text = ax.text(j, i, interclass_matrix[i, j],
                            ha="center", va="center", color="w")
                
                
                plt.savefig(fig_path)
                plt.clf()
                # st()

draw_heatmap_expconfig()
# draw_posneg_weight_cmp_hist()