import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def read_csv_data(csv_path):
    df = pd.read_csv(csv_path)

    methods = df["Method Name"].tolist()
    model_values = df.drop(columns=["Method Name"]).values.tolist()
    categories = df.columns[1:].tolist()  # Skip 'Method Name'

    # Split categories into hierarchical structure
    x_main = [cat.split("_")[-1] for cat in categories]  # CPU->CPU, CPU->GPU
    x_sub = [cat.split("_")[0] for cat in categories]  # AdaBoost, Bagging, etc.
    x_values = [x_main, x_sub]

    return methods, model_values, x_values


def generate_colors(n):
    base_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#ED7D31"]
    return base_colors * (n // len(base_colors) + 1)


def plot_model_comparison_from_csv(csv_path, output_file="model_comparison_from_csv.pdf"):
    methods, model_values, x_values = read_csv_data(csv_path)
    colors = generate_colors(len(methods))

    fig = go.Figure()

    for method, values, color in zip(methods, model_values, colors):
        fig.add_bar(name=method, x=x_values, y=values, marker_color=color)

    fig.update_layout(
        barmode="group",
        xaxis=dict(
            tickangle=0,
            showgrid=False,
            title_font=dict(size=20),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title="Average MAPE (Lower is better)",
            showgrid=True,
            range=[0, 300],  # Or auto-scale based on max values
            title_font=dict(size=20),
            tickfont=dict(size=14)
        ),
        legend_title=None,
        template="plotly_white",
        legend=dict(
            x=0.25,
            y=0.7,
            xanchor="center",
            yanchor="bottom",
            orientation="v",
            font=dict(size=15)
        ),
        margin=dict(t=30, b=30, l=20, r=20),
    )

    pio.kaleido.scope.mathjax = False
    fig.write_image(output_file, format="pdf")
    fig.show()


# ✅ Usage Example:
# Place your CSV file path below
csv_file_path = "plotly_sample_data.csv"
plot_model_comparison_from_csv(csv_file_path)
