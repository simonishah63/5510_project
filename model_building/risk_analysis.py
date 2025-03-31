import numpy as np
import matplotlib.pyplot as plt

def analyze_risk(tech_rets):
    """Analyze risk vs expected return"""
    rets = tech_rets.dropna()
    
    area = np.pi * 20
    plt.figure(figsize=(10, 8))
    plt.scatter(rets.mean(), rets.std(), s=area)
    plt.xlabel('Expected return')
    plt.ylabel('Risk')
    
    for label, x, y in zip(rets.columns, rets.mean(), rets.std()):
        plt.annotate(label, xy=(x, y), xytext=(50, 50), textcoords='offset points',
                    ha='right', va='bottom',
                    arrowprops=dict(arrowstyle='-', color='blue', connectionstyle='arc3,rad=-0.3'))
    
    plt.show()