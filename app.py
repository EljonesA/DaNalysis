from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyrebase
from config import firebaseConfig
import pandas as pd
import plotly.express as px
import datetime
import stripe

app = Flask(__name__)
app.secret_key = 'secrt7436-tehdhhe'
stripe.api_key = 'sk_test_51Pn2ifK4FVOPIRC2iy1vtQfyHkbWI6S8CdXlWbMO1DPujPtlUgoSu3e4s9IvKyMDhsqGe3RAFuzWusUVZrliMv8d00HVfNHReK'

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login functionality.

    Renders the login page on GET request.
    On POST request, attempts to authenticate the user using Firebase with the provided
    email and password. If authentication is successful, the user is redirected to the 
    landing page. If authentication fails, an error message is displayed.

    Returns:
        str: HTML template for the login page or a redirect to the landing page.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']
            return redirect(url_for('landing_page'))
        except:
            return "Login failed. Please check your credentials."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup functionality.

    Renders the signup page on GET request.
    On POST request, attempts to create a new user account in Firebase with the provided 
    email and password. If the signup is successful, the user is redirected to the login page. 
    If passwords do not match or signup fails, an error message is displayed.

    Returns:
        str: HTML template for the signup page or a redirect to the login page.
    """
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
    """
    Log out the currently logged-in user.
    Clears the user session and redirects to the login page.

    Returns:
        str: Redirect to the login page.
    """
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def landing_page():
    """
    Render the landing page for authenticated users.
    If the user is not logged in, they are redirected to the login page.

    Returns:
        str: HTML template for the landing page or a redirect to the login page.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('landing_Page.html')


''' =====> Macroeconomic Analysis routes & logic <===== '''
@app.route('/macroeconomic_analysis')
def macroeconomic_analysis():
    """
    Render the Macroeconomic Analysis page.
    If the user is not logged in, they are redirected to the login page.

    Returns:
        str: HTML template for the Macroeconomic Analysis page or a redirect to the login page.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('macroeconomic_analysis.html')

# filters
@app.route('/fetch_filtered_data')
def fetch_filtered_data():
    """
    Fetch and filter Nominal GDP, Historical Population, or GDP Per Capita data.

    Based on the selected chart type ('gdp', 'population', 'per_capita') and period ('5Y', '10Y', 'Full'),
    this function reads the corresponding dataset, filters it, generates a Plotly chart, and returns 
    the chart as HTML.

    Returns:
        json: JSON object containing the HTML of the generated Plotly chart or an error message.
    """
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
    """
    Fetch and filter exchange rate data.

    Based on the selected period ('5Y', '2Y', 'YTD', '3M', '1M', 'Full'), this function reads the exchange 
    rate dataset, filters it, generates a Plotly chart, and returns the chart as HTML.

    Returns:
        json: JSON object containing the HTML of the generated Plotly chart or an error message.
    """
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
    """
    Fetch and filter inflation rate data.

    Based on the selected period ('3M', '1M', 'Full'), this function reads the inflation rate dataset, 
    filters it, generates a Plotly chart, and returns the chart as HTML.

    Returns:
        json: JSON object containing the HTML of the generated Plotly chart or an error message.
    """
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
    """
    Fetch and filter share prices data.

    Based on the selected period ('2M', '5D', 'Full'), this function reads the share prices dataset, 
    filters it, generates a Plotly chart, and returns the chart as HTML.

    Returns:
        json: JSON object containing the HTML of the generated Plotly chart or an error message.
    """
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
    """
    Fetch and filter share prices data.

    Based on the selected period ('3M', '1M', '5D', 'Full'), this function reads the share prices dataset, 
    filters it, generates a Plotly chart, and returns the chart as HTML.

    Returns:
        json: JSON object containing the HTML of the generated Plotly chart or an error message.
    """
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
    """
    Render the first dashboard showing Nominal GDP, Population Trend, and GDP Per Capita.

    If the user is not logged in, they are redirected to the login page.
    This route reads CSV data for each metric, generates Plotly visualizations, 
    and renders them in the 'dashboard1.html' template.

    Returns:
        str: HTML template for the first dashboard with embedded Plotly graphs.
    """
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
    """
    Render the second dashboard showing USD/KES exchange rates.

    If the user is not logged in, they are redirected to the login page.
    This route reads CSV data for exchange rates, generates a Plotly visualization, 
    and renders it in the 'dashboard2.html' template.

    Returns:
        str: HTML template for the second dashboard with an embedded Plotly graph.
    """
    if 'user' not in session:
        return redirect(url_for('login'))

    # Exchange rates processing & plotting
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
    """
    Render the third dashboard with premium content.

    If the user is not logged in, they are redirected to the login page.
    The template 'dashboard3.html' will contain the premium content, 
    and access will be controlled by the user's subscription status.

    Returns:
        str: HTML template for the third dashboard.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard3.html')

@app.route('/inflation_monthly')
def inflation_monthly():
    """
    Render the page comparing current month's inflation vs. prior month's inflation.

    If the user is not logged in, they are redirected to the login page.
    This route reads CSV data for monthly inflation rates, generates a Plotly bar chart, 
    and renders it in the 'inflation_comparison.html' template.

    Returns:
        str: HTML template with an embedded Plotly graph comparing monthly inflation.
    """
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
    """
    Render the page showing the historical inflation trend (premium content).

    If the user is not logged in, they are redirected to the login page.
    The 'is_premium' parameter determines whether the user has access to premium content.
    This route reads CSV data for inflation rates, generates a Plotly line chart, 
    and renders it in the 'inflation_premium.html' template.

    Returns:
        str: HTML template with an embedded Plotly graph showing the inflation trend.
    """
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
    """
    Render the paywall page for premium content access.

    This route serves the 'paywall.html' template, which prompts the user 
    to select a payment method to gain access to premium content.

    Returns:
        str: HTML template for the paywall.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('paywall.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    """
    Handle payment processing for premium content access.

    Depending on the selected payment method, this route handles the payment via Stripe 
    for Visa or integrates with M-Pesa SDK for mobile payments.
    If payment is successful, the user is redirected to access premium content.

    Returns:
        str: Redirect to the inflation trend page if payment is successful,
             or to the paywall page if payment fails.
    """
    payment_method = request.form.get('payment')

    if payment_method == 'visa':
        # Get form data including stripe token
        token = request.form['stripeToken']
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        price = request.form['total_price']

        try:
            if (int(price) == 0):
                desc = "DaNalysis Premium Membership (Coupon applied) - Inflation"
            else:
                desc = "DaNalysis Premium Membership - Inflation"
            # Create a charge using the token
            charge = stripe.Charge.create(
                amount=10000,  # Amount in cents
                currency='kes',
                description=desc,
                source=token,
                metadata={
                    'customer_name': customer_name,
                    'customer_address': customer_address
                }
            )
            return redirect(url_for('inflation_trend', is_premium=True))
        except stripe.error.StripeError as e:
            return redirect(url_for('paywall'))
    elif payment_method == 'mpesa':
        print("MPESA method")
        full_name = request.form['full_name']
        mobile_number = request.form['mobile_number']
        # Integrate with M-Pesa SDK here
        flash('M-Pesa payment initiated! Follow the instructions on your phone.', 'success')
        return redirect(url_for('inflation_trend', is_premium=True))

@app.route('/paywall_shares')
def paywall_shares():
    """
    Render the paywall page for premium content access.

    This route serves the 'paywall.html' template, which prompts the user 
    to select a payment method to gain access to premium content.

    Returns:
        str: HTML template for the paywall.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('paywall_shares.html')

@app.route('/process_payment_shares', methods=['POST'])
def process_payment_shares():
    """
    Handle payment processing for premium content access.

    Depending on the selected payment method, this route handles the payment via Stripe 
    for Visa or integrates with M-Pesa SDK for mobile payments.
    If payment is successful, the user is redirected to access premium content.

    Returns:
        str: Redirect to the inflation trend page if payment is successful,
             or to the paywall page if payment fails.
    """
    payment_method = request.form.get('payment')

    if payment_method == 'visa':
        # Get form data including stripe token
        token = request.form['stripeToken']
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        price = request.form['total_price']

        try:
            if (int(price) == 0):
                desc = "DaNalysis Premium Membership (Coupon applied) - Shares"
            else:
                desc = "DaNalysis Premium Membership - Shares"
            # Create a charge using the token
            charge = stripe.Charge.create(
                amount=10000,  # Amount in cents
                currency='kes',
                description=desc,
                source=token,
                metadata={
                    'customer_name': customer_name,
                    'customer_address': customer_address
                }
            )
            return redirect(url_for('page2', is_premium=True))
        except stripe.error.StripeError as e:
            return redirect(url_for('paywall'))
    elif payment_method == 'mpesa':
        print("MPESA method")
        full_name = request.form['full_name']
        mobile_number = request.form['mobile_number']
        # Integrate with M-Pesa SDK here
        flash('M-Pesa payment initiated! Follow the instructions on your phone.', 'success')
        return redirect(url_for('page2', is_premium=True))


''' =====> Financial Analysis routes & logic <===== '''

@app.route('/financial_analysis')
def financial_analysis():
    """
    Render the Financial Analysis page.

    If the user is not logged in, they are redirected to the login page.
    This route serves the 'financial_analysis.html' template, which provides 
    financial analysis tools and content for the user.

    Returns:
        str: HTML template for the Financial Analysis page.
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('financial_analysis.html')

@app.route('/page1')
def page1():
    """
    Render the first financial analysis page showing July To Date Safaricom Share Prices.

    If the user is not logged in, they are redirected to the login page.
    This route reads CSV data for share prices, generates a Plotly line chart, 
    and renders it in the 'page1.html' template.

    Returns:
        str: HTML template with an embedded Plotly graph showing share prices.
    """
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
    """
    Render the second financial analysis page showing June To Date Safaricom Share Prices.

    If the user is not logged in, they are redirected to the login page.
    This route reads CSV data for share prices, generates a Plotly line chart, 
    and renders it in the 'page2.html' template.

    Returns:
        str: HTML template with an embedded Plotly graph showing share prices.
    """
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