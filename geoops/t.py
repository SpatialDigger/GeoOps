import dash
from dash import dcc
from dash import html
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'Fruit': ['Apple', 'Banana', 'Orange', 'Grapes'],
    'Color': ['Red', 'Yellow', 'Orange', 'Purple'],
    'Price': [0.5, 0.3, 0.4, 0.8]
})

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Dropdown(
        id='fruit-dropdown',  # ID of the dropdown component
        options=[{'label': fruit, 'value': fruit} for fruit in df['Fruit']],  # Dropdown options
        value=None,  # Initial value of the dropdown
        placeholder='Select a fruit...',  # Placeholder text
    ),
    html.Table(id='filtered-data-table'),  # Table to display filtered data
])

# Define a callback function for the dropdown menu
@app.callback(
    dash.dependencies.Output('filtered-data-table', 'children'),  # Output to update the table
    [dash.dependencies.Input('fruit-dropdown', 'value')]  # Input from the dropdown
)
def update_table(selected_fruit):
    if selected_fruit:
        filtered_df = df[df['Fruit'] == selected_fruit]
        return generate_table(filtered_df)
    else:
        return generate_table(df)

# Helper function to generate a Dash table from a DataFrame
def generate_table(df):
    table = html.Table(
        # Table header
        [html.Tr([html.Th(col) for col in df.columns])] +
        # Table rows
        [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))]
    )
    return table

if __name__ == '__main__':
    app.run_server(debug=True)  # Run the Dash app
