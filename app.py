# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyrebase
from config import firebaseConfig
import pandas as pd
import plotly.express as px
import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"{email}: {password}")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']
            return redirect(url_for('landing_page'))
        except:
            return "Login failed. Please check your credentials."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            try:
                auth.create_user_with_email_and_password(email, password)
                return redirect(url_for('login'))
            except:
                return "Sign up failed. Please try again."
        else:
            return "Passwords do not match."
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def landing_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('landing_Page.html')


''' =====> Macroeconomic Analysis routes & logic <===== '''
@app.route('/macroeconomic_analysis')
def macroeconomic_analysis():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('macroeconomic_analysis.html')

# filters
@app.route('/fetch_filtered_data')
def fetch_filtered_data():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_type = request.args.get('chart_type')
    period = request.args.get('period')

    # Fetch the appropriate data based on chart type and period
    if chart_type == 'gdp':
        df = pd.read_csv('datasets/Nominal_GDP_data.csv')
    elif chart_type == 'population':
        df = pd.read_csv('datasets/Historical_Population_Data.csv')
    elif chart_type == 'per_capita':
        df = pd.read_csv('datasets/GDP_Per_Capita.csv')
    else:
        return jsonify({"error": "Invalid chart type"}), 400

    # Filter data based on the period (5Y, 10Y, Full)
    if period == '5Y':
        df = df.tail(5)
    elif period == '10Y':
        df = df.tail(10)
    # 'Full' would just use the entire dataset

    # Generate the appropriate Plotly figure
    if chart_type == 'gdp':
        fig = px.line(df, x='Year', y='GDP')
    elif chart_type == 'population':
        fig = px.bar(df, x='Year', y='Population')
    elif chart_type == 'per_capita':
        fig = px.scatter(df, x='Year', y='GDP per capita')

    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )

    # Return the HTML of the plot
    return jsonify({"graph_html": fig.to_html(full_html=False)})

@app.route('/fetch_filtered_exchanges')
def fetch_filtered_exchanges():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_type = request.args.get('chart_type')
    period = request.args.get('period')

    # Fetch the appropriate data
    if chart_type == 'exchange':
        df = pd.read_csv('datasets/Exchange_Rates.csv')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)  # ensure date in datetime format
    else:
        return jsonify({"error": "Invalid chart type"}), 400

    # Get today's date
    today = pd.to_datetime(datetime.date.today())

    # Filter data based on the period
    if period == '5Y':
        start_date = today - pd.DateOffset(years=5)
        df = df[df['Date'] >= start_date]
    elif period == '2Y':
        start_date = pd.to_datetime(f'{today.year - 1}-01-01')  # beginning of last yr
        df = df[df['Date'] >= start_date]
    elif period == 'YTD':
        start_date = pd.to_datetime(f'{today.year}-01-01')  # Beginning of this year
        df = df[df['Date'] >= start_date]
    elif period == '3M':
        start_date = today - pd.DateOffset(months=3)
        df = df[df['Date'] >= start_date]
    elif period == '1M':
        start_date = today - pd.DateOffset(months=1)
        df = df[df['Date'] >= start_date]
    # 'Full' would just use the entire dataset

    # Generate the filtered Plotly figure
    fig = px.line(df, x='Date', y='Mean')

    # Ensure the x-axis is displayed by individual dates
    fig.update_xaxes(type='date')

    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )

    # Return the HTML of the plot
    return jsonify({"graph_html": fig.to_html(full_html=False)})

@app.route('/fetch_filtered_inflation')
def fetch_filtered_inflation():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_type = request.args.get('chart_type')
    period = request.args.get('period')

    # Read Dataset
    df = pd.read_csv('datasets/Inflation_Rates.csv')

    # Filter data based on the period
    if period == '3M':
        df = df.tail(3)
        fig = px.bar(df, x='Month', y='12-Month Inflation')
    elif period == '1M':
        df = df.tail(1)
        fig = px.bar(df, x='Month', y='12-Month Inflation')
    else:  # Default to YTD or full dataset
        fig = px.line(df, x='Month', y='12-Month Inflation')

    # Customize the layout
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )

    # Return the HTML of the plot
    return jsonify({"graph_html": fig.to_html(full_html=False)})

@app.route('/fetch_filtered_shares')
def fetch_filtered_shares():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_type = request.args.get('chart_type')
    period = request.args.get('period')

    # Fetch the appropriate data
    if chart_type == 'exchange':
        df = pd.read_csv('datasets/Share_Prices_July_TD.csv')
        df['Date'] = pd.to_datetime(df['Date'], format='mixed')  # ensure date is in datetime format
    else:
        return jsonify({"error": "Invalid chart type"}), 400

    # Get today's date
    today = pd.to_datetime(datetime.date.today())

    # Filter data based on the period
    if period == '2M':
        start_date = today - pd.DateOffset(days=60)
        df = df[df['Date'] >= start_date]
    elif period == '5D':
        start_date = today - pd.DateOffset(days=5)
        df = df[df['Date'] >= start_date]
    # 'Full' would just use the entire dataset

    # Generate the filtered Plotly figure
    fig = px.line(df, x='Date', y=' Close')

    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )

    # Return the HTML of the plot
    return jsonify({"graph_html": fig.to_html(full_html=False)})

@app.route('/fetch_filtered_shares_more')
def fetch_filtered_shares_more():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_type = request.args.get('chart_type')
    period = request.args.get('period')

    # Fetch the appropriate data
    if chart_type == 'exchange':
        df = pd.read_csv('datasets/Share_Prices_June_TD.csv')
        df['Date'] = pd.to_datetime(df['Date'], format='mixed')  # ensure date is in datetime format
    else:
        return jsonify({"error": "Invalid chart type"}), 400

    # Get today's date
    today = pd.to_datetime(datetime.date.today())

    # Filter data based on the period
    if period == '3M':
        start_date = today - pd.DateOffset(days=90)
        df = df[df['Date'] >= start_date]
    elif period == '1M':
        start_date = today - pd.DateOffset(days=30)
        df = df[df['Date'] >= start_date]
    elif period == '5D':
        start_date = today - pd.DateOffset(days=5)
        df = df[df['Date'] >= start_date]
    # 'Full' would just use the entire dataset

    # Generate the filtered Plotly figure
    fig = px.line(df, x='Date', y=' Close')

    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )

    # Return the HTML of the plot
    return jsonify({"graph_html": fig.to_html(full_html=False)})

@app.route('/dashboard1')
def dashboard1():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Nominal GDP processing & ploting
    df = pd.read_csv('datasets/Nominal_GDP_data.csv')
    fig = px.line(df, x='Year', y='GDP')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(line_color='green')  # plot line color
    gdp_graph_html = fig.to_html(full_html=False)

    # Population trend processing & plotting
    df = pd.read_csv('datasets/Historical_Population_Data.csv')
    fig = px.bar(df, x='Year', y='Population')
    fig.update_layout(plot_bgcolor='white')
    fig.update_traces(marker_color='#132e57')
    population_graph_html = fig.to_html(full_html=False)

    # GDP Per Capita processing & plotting
    df = pd.read_csv('datasets/GDP_Per_Capita.csv')
    fig = px.scatter(df, x='Year', y='GDP per capita')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(marker=dict(color='orange'))
    per_capita_graph_html = fig.to_html(full_html=False)

    return render_template(
        'dashboard1.html',
        gdp_graph_html=gdp_graph_html,
        population_graph_html=population_graph_html,
        per_capita_graph_html=per_capita_graph_html
    )

@app.route('/dashboard2')
def dashboard2():
    if 'user' not in session:
        return redirect(url_for('login'))
    # GDP Per Capita processing & plotting
    df = pd.read_csv('datasets/Exchange_Rates.csv')
    fig = px.line(df, x='Date', y='Mean')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(marker=dict(color='orange'))
    exchange_rates_graph_html = fig.to_html(full_html=False)
    return render_template('dashboard2.html', exchange_rates_graph_html=exchange_rates_graph_html)

@app.route('/dashboard3')
def dashboard3():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard3.html')

@app.route('/inflation_monthly')
def inflation_monthly():
    # freely accessible page
    if 'user' not in session:
        return redirect(url_for('login'))

    # Current vs Prior Month inflation processing & plotting
    df = pd.read_csv('datasets/Month_Over_Month_Inflation Rates.csv')
    fig = px.bar(df, x='Month', y='12-Month Inflation')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(marker=dict(color='orange'))
    month_over_month_graph_html = fig.to_html(full_html=False)
    return render_template(
        'inflation_comparison.html',
        month_over_month_graph_html=month_over_month_graph_html
    )

@app.route('/inflation_trend')
def inflation_trend():
    # premium content page
    if 'user' not in session:
        return redirect(url_for('login'))

    # Set is a full member
    is_premium = request.args.get('is_premium', False, type=bool)

    # inflation trend processing & plotting
    df = pd.read_csv('datasets/Inflation_Rates.csv')
    fig = px.line(df, x='Month', y='12-Month Inflation')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(marker=dict(color='orange'))
    inflation_trend_graph_html = fig.to_html(full_html=False)
    return render_template(
        'inflation_premium.html',
        inflation_trend_graph_html=inflation_trend_graph_html,
        is_premium=is_premium
    )

@app.route('/paywall')
def paywall():
    return render_template('paywall.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    full_name = request.form['full_name']
    address = request.form['address']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    # Here you would integrate with a payment gateway to process the payment
    # For example, using Stripe:
    # stripe.Charge.create(
    #     amount=amount_in_cents,
    #     currency='usd',
    #     source=card_token,
    #     description='Premium Membership'
    # )

    # Assuming payment is successful:
    flash('Payment successful! You are now a premium member.', 'success')
    return redirect(url_for('inflation_trend', is_premium=True))


''' =====> Financial Analysis routes & logic <===== '''

@app.route('/financial_analysis')
def financial_analysis():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('financial_analysis.html')

@app.route('/page1')
def page1():
    if 'user' not in session:
        return redirect(url_for('login'))

    # July To Date Safaricom Share Prices processing & ploting
    df = pd.read_csv('datasets/Share_Prices_July_TD.csv')
    fig = px.line(df, x='Date', y=' Close')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(line_color='blue')  # plot line color
    share_prices_graph_html = fig.to_html(full_html=False)

    return render_template(
        'page1.html',
        share_prices_graph_html=share_prices_graph_html
    )

@app.route('/page2')
def page2():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Set is a full member
    is_premium = request.args.get('is_premium', False, type=bool)

    # July To Date Safaricom Share Prices processing & ploting
    df = pd.read_csv('datasets/Share_Prices_June_TD.csv')
    fig = px.line(df, x='Date', y=' Close')
    fig.update_layout(
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.1, griddash='dot')
    )
    fig.update_traces(line_color='blue')  # plot line color
    share_prices_graph_html = fig.to_html(full_html=False)

    return render_template(
        'page2.html',
        share_prices_graph_html=share_prices_graph_html,
        is_premium=is_premium
    )



if __name__ == '__main__':
    app.run(debug=True)