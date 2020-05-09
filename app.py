# -*- encoding: utf-8 -*-

from flask import Flask, redirect, url_for, request, render_template, g
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go



app = Flask(__name__)
global check
global user
check = False
user = None

@app.route('/index', methods=['GET', 'POST'])
def index():
    global check
    global user
    if check:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        user = request.form['id']
        password = request.form['password']
        if user == 'jino' and password == '1234':
            check = True
            return redirect(url_for('home'))
        return render_template('index.html', error="Wrong username or password")
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    global check
    global user
    if not check:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if 'Sign out' in request.form:
            check = False
            user = None
            return redirect(url_for('index'))
        else:
            return redirect('/dashboard')
    return render_template('home.html', username=user)


df = pd.read_excel(
    "https://github.com/KaistZelatore/IE481_1_TestGithub/blob/master/covid-19-example.xlsx?raw=True"
)

app2 = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
cities = df["City"].unique()

app2.layout = html.Div([
    html.H2("Corona Report"),
    html.Div(
        [
            dcc.Dropdown(
                id="City",
                options=[{
                    'label': i,
                    'value': i
                } for i in cities], value = 'All cities'),
        ],
        style={'width': '25%', 'display': 'inline-block'}),
    dcc.Graph(id='corona'),
])


@app2.callback(
    dash.dependencies.Output('corona', 'figure'),
    [dash.dependencies.Input('City', 'value')])
def update_graph(City):
    if City == "All cities":
        df_plot = df.copy()
    else:
        df_plot = df[df['City'] == City]

    pv = pd.pivot_table(
        df_plot,
        index=["AgeGroup"],
        columns=["Status"],
        values=["Population"],
        aggfunc=sum,
        fill_value=0 )

    trace3 = go.Bar(x=pv.index, y=pv[('Population', 'Active')], name = 'Active')
    trace2 = go.Bar(x=pv.index, y=pv[('Population', 'Recovered')], name = 'Recovered')
    trace1 = go.Bar(x=pv.index, y=pv[('Population', 'Death')], name='Death')

    return {
        'data': [trace1, trace2, trace3],
        'layout': go.Layout(
            title="People's Status for {}".format(City),
            barmode='stack')
    }


if __name__ == '__main__':
    app.run(debug = True)