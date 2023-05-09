import seaborn as sns
import pandas as pd

# create some sample data
data = pd.DataFrame({
    'group': ['A', 'B', 'C', 'D'],
    'variable_1': [20, 10, 30, 15],
    'variable_2': [10, 30, 20, 25],
    'variable_3': [5, 15, 25, 20]
})

def group_bar(data):

    # Define the data
    data = {
        'Year': ['2019', '2020', '2021'],
        'Apples': [50, 80, 100],
        'Oranges': [20, 50, 70],
        'Bananas': [30, 70, 80]
    }
    df = pd.DataFrame(data)

    # Melt the data to a long format
    df_melt = pd.melt(df, id_vars=['Year'], var_name='Fruit', value_name='Value')

    # Set the aesthetic mappings
    aesthetics = {
        'x': 'Year',
        'y': 'Value',
        'hue': 'Fruit',
        'palette': 'bright'
    }

    # Create the stacked bar chart
    sns.set_style('whitegrid')
    g = sns.catplot(
        data=df_melt,
        kind='bar',
        **aesthetics,
        ci=None,
        height=6,
        aspect=1.5
    )
    g.despine(left=True)
    g.set_axis_labels('Year', 'Fruit Sales')
    g.legend.set_title('Fruit')


def stacked_bar(data):
    import seaborn as sns
    import pandas as pd

    # Define the data
    data = {
        'Year': ['2019', '2020', '2021'],
        'Apples': [50, 80, 100],
        'Oranges': [20, 50, 70],
        'Bananas': [30, 70, 80]
    }
    df = pd.DataFrame(data)

    # Set the aesthetic mappings
    aesthetics = {
        'x': 'Year',
        'y': ['Apples', 'Oranges', 'Bananas'],
        'palette': 'bright'
    }

    # Create the stacked bar chart
    sns.set_style('whitegrid')
    g = sns.catplot(
        data=df,
        kind='bar',
        **aesthetics,
        ci=None,
        height=6,
        aspect=1.5
    )
    g.despine(left=True)
    g.set_axis_labels('Year', 'Fruit Sales')
    g.legend.set_title('Fruit')
    g.ax.set_ylim(0, 300)
