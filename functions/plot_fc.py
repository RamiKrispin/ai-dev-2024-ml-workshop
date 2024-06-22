import plotly.graph_objects as go

def plot_fc(actual,forecast, actual_length = None):
    
    if actual_length is not None:
        actual = actual.tail(n = actual_length)

    p = go.Figure([
        go.Scatter(
            name="Actual",
            x= actual["period"], 
            y= actual["value"],
            mode='lines',
            line= dict(color='royalblue'),
        ), 
        go.Scatter(
            name="Forecast",
            x= forecast["period"], 
            y= forecast[0.5],
            mode='lines',
            line= dict(color='black', dash = "dash"),
        ),
        go.Scatter(
            name= "Prediction Intervals",
            x= forecast["period"], 
            y= forecast[0.95],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=True
        ),
        go.Scatter(
            name="Prediction Intervals",
            x= forecast["period"], 
            y= forecast[0.05],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])

    return p 
