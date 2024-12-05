import altair as alt
import pandas as pd
from vega_datasets import data

df = pd.read_csv("data.csv")


# selections
country_select = alt.selection_point(
    name="selector",
    fields=["Country", "id"],
)
continent_select = alt.selection_point(name="continent_selector", fields=["Continent"])

# continent filter
list_of_continents: list[str] = sorted(df["Continent"].unique().tolist())
list_of_continents.insert(0, "All")
continent_dropdown = alt.binding_select(
    options=list_of_continents, name="Filter data by Continent: "
)
continent_filtering = alt.param(name="filtering", bind=continent_dropdown, value="All")


# map graph
df_urban = df.copy()
df_urban["percentage_urban_population"] = (
    df_urban["Urban_population"] / df_urban["Population"] * 100
)

topo_country_shapes = alt.topo_feature(data.world_110m.url, "countries")

basemap = alt.layer(
    alt.Chart(alt.sphere()).mark_geoshape(fill="white"),
    alt.Chart(alt.graticule()).mark_geoshape(stroke="LightGray", strokeWidth=0.5),
)

countries = alt.Chart(topo_country_shapes).mark_geoshape(
    fill="LightGray", stroke="white"
)

bubbles = (
    alt.Chart(topo_country_shapes)
    .mark_circle(stroke="black", opacity=0.9)
    .transform_lookup(
        lookup="id",
        from_=alt.LookupData(
            data=df_urban,
            key="id",
            fields=[
                "Longitude",
                "Latitude",
                "Country",
                "Continent",
                "Density (P/Km2)",
                "percentage_urban_population",
            ],
        ),
    )
    .encode(
        longitude="Longitude:Q",
        latitude="Latitude:Q",
        color=alt.condition(
            country_select & continent_select,
            alt.Color(
                "percentage_urban_population:Q",
                scale=alt.Scale(scheme="purples", type="linear", domain=[0, 100]),
                legend=alt.Legend(
                    gradientLength=113,
                    direction="horizontal",
                    orient="right",
                ),
                title="Urban Population (%)",
            ),
            alt.value("lightgray"),
        ),
        strokeWidth=alt.condition(
            (country_select & continent_select),
            alt.value(2),
            alt.value(0.5),
        ),
        size=alt.Size(
            "Density (P/Km2):Q",
            scale=alt.Scale(range=[30, 1500]),
            legend=alt.Legend(title="Density (P/Km2)"),
        ),
        tooltip=[
            "Country:N",
            alt.Tooltip(
                "percentage_urban_population:Q",
                title="Urban Population (%)",
                format=".2f",
            ),
            "Density (P/Km2):Q",
        ],
    )
    .transform_filter(
        (alt.datum.Continent == continent_filtering) | (continent_filtering == "All")
    )
    .add_params(country_select, continent_select, continent_filtering)
)
map_graph = (basemap + countries + bubbles).project("equalEarth")


# health Analysis
df_health = df.copy()
df_health["GDP per capita (in $)"] = df_health["GDP (in $)"] / df_health["Population"]
df_health = df_health.dropna(
    subset=[
        "Life expectancy",
        "Physicians per thousand",
        "GDP per capita (in $)",
        "GDP (in $)",
    ],
    axis="index",
)

health_analysis = (
    alt.Chart(df_health)
    .mark_circle(size=100, stroke="black", opacity=0.9)
    .encode(
        x=alt.X(
            "GDP per capita (in $):Q",
            title="GDP per capita (in $)",
            scale=alt.Scale(
                domain=[0, max(df_health["GDP per capita (in $)"]) * (21 / 20)]
            ),
        ),
        y=alt.Y(
            "Life expectancy:Q",
            title="Life Expectancy",
            scale=alt.Scale(domain=[0, max(df_health["Life expectancy"]) * (21 / 20)]),
        ),
        color=alt.condition(
            (country_select & continent_select),
            alt.Color(
                "Physicians per thousand:Q",
                scale=alt.Scale(scheme="viridis"),
                legend=alt.Legend(
                    title="Physicians per Thousand",
                    gradientLength=300,
                    gradientThickness=20,
                ),
            ),
            alt.value("lightgray"),
        ),
        strokeWidth=alt.condition(
            (country_select & continent_select),
            alt.value(2),
            alt.value(0.5),
        ),
        size=alt.Size(
            "Physicians per thousand:Q",
            scale=alt.Scale(range=[30, 1500]),
            legend=alt.Legend(title="Physicians per Thousand"),
        ),
        tooltip=[
            "Country",
            "Life expectancy",
            alt.Tooltip("GDP per capita (in $)", format=",.2f"),
            "Physicians per thousand",
        ],
    )
    .transform_filter(
        (alt.datum.Continent == continent_filtering) | (continent_filtering == "All")
    )
    .add_params(country_select, continent_select, continent_filtering)
    .interactive(name="move_axis_y", bind_x=False)
)

# CO2 emissions scatter
area_df = df.copy()
area_df = area_df.dropna(
    subset=[
        "GDP (in $)",
        "Land Area(Km2)",
        "Co2-Emissions",
    ],
    axis="index",
)
co2_emissions_scatter = (
    alt.Chart(area_df)
    .mark_circle(size=100, stroke="black", strokeWidth=0.5, opacity=0.9)
    .encode(
        x=alt.X(
            "GDP (in $):Q",
            title="GDP (in $)",
            scale=alt.Scale(domain=[0, max(area_df["GDP (in $)"]) * (21 / 20)]),
        ),
        y=alt.Y(
            "Land Area(Km2):Q",
            title="Land Area (Km2)",
            scale=alt.Scale(domain=[0, max(area_df["Land Area(Km2)"]) * (21 / 20)]),
        ),
        color=alt.condition(
            country_select & continent_select,
            alt.Color(
                "Co2-Emissions:Q",
                scale=alt.Scale(
                    scheme="magma",
                    domain=[
                        0,
                        area_df["Co2-Emissions"].max(),
                    ],
                ),
                legend=alt.Legend(
                    title="Co2 Emissions",
                    gradientLength=500,
                    gradientThickness=100,
                ),
                title="Co2 Emissions",
            ),
            alt.value("lightgray"),
        ),
        size=alt.Size(
            "Co2-Emissions:Q",
            title="Co2 Emissions",
            scale=alt.Scale(
                domain=[
                    0,
                    area_df["Co2-Emissions"].max(),
                ],
                range=[30, 1500],
            ),
            legend=alt.Legend(
                title="Co2 Emissions",
                gradientLength=500,
                gradientThickness=100,
            ),
        ),
        strokeWidth=alt.condition(
            (country_select & continent_select),
            alt.value(2),
            alt.value(0.5),
        ),
        tooltip=[
            "Country:N",
            alt.Tooltip("GDP (in $):Q", format=",.2f"),
            alt.Tooltip("Co2-Emissions:Q", format=","),
            alt.Tooltip("Land Area(Km2):Q", format=","),
        ],
    )
    .transform_filter(
        (alt.datum.Continent == continent_filtering) | (continent_filtering == "All")
    )
    .add_params(country_select, continent_select, continent_filtering)
    .interactive(bind_x=False)
)


# correlation matrix
df["GDP per capita (in $)"] = df_health["GDP per capita (in $)"]
df["percentage_urban_population"] = df_urban["percentage_urban_population"]

used_variables = [
    "Life expectancy",
    "GDP per capita (in $)",
    "Physicians per thousand",
    "percentage_urban_population",
    "Density (P/Km2)",
    "GDP (in $)",
    "Land Area(Km2)",
    "Co2-Emissions",
]
df_clean = df[used_variables].copy()
shown_names = [
    "Urban Population (%)",
    "Land Area (Km2)",
]
df_clean.rename(
    columns={
        "percentage_urban_population": "Urban Population (%)",
        "Land Area(Km2)": "Land Area (Km2)",
    },
    inplace=True,
)
correlation_matrix = df_clean.corr().reset_index().melt(id_vars="index")
correlation_matrix.columns = ["Variable1", "Variable2", "Correlation"]

heatmap = (
    alt.Chart(correlation_matrix)
    .mark_rect()
    .encode(
        x=alt.X("Variable1:O", title="", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Variable2:O", title="", axis=alt.Axis(labelAngle=0)),
        color=alt.Color(
            "Correlation:Q",
            scale=alt.Scale(scheme="reds"),
            legend=alt.Legend(
                title="Correlation Value",
                orient="right",
                direction="horizontal",
                gradientLength=93,
            ),
        ),
        tooltip=["Variable1", "Variable2", "Correlation"],
    )
)

text = heatmap.mark_text(baseline="middle").encode(
    text=alt.Text("Correlation:Q", format=".2f"),
    color=alt.condition(
        alt.datum.Correlation > 0.5, alt.value("black"), alt.value("white")
    ),
)
correlation_chart = heatmap + text

# bar chart
continent_gdp = df.groupby("Continent")["GDP (in $)"].mean().reset_index()
gdp_bar_chart = (
    alt.Chart(
        continent_gdp,
    )
    .mark_bar(stroke="black", strokeWidth=0.5)
    .encode(
        x=alt.X(
            "Continent:N",
            title="Continent",
            axis=alt.Axis(labelAngle=0),
            sort=alt.EncodingSortField(field="GDP (in $)", order="descending"),
        ),
        y=alt.Y(
            "GDP (in $):Q",
            title="Average GDP (in $)",
            scale=alt.Scale(domain=[0, max(continent_gdp["GDP (in $)"]) * (21 / 20)]),
        ),
        color=alt.condition(
            continent_select,
            alt.Color("GDP (in $):Q", legend=None, scale=alt.Scale(scheme="greens")),
            alt.value("lightgray"),
        ),
        # strokeWidth=alt.condition(
        #     (continent_select),
        #     alt.value(2),
        #     alt.value(0.5),
        # ),
        tooltip=[
            alt.Tooltip("Continent:N", title="Continent"),
            alt.Tooltip("GDP (in $):Q", title="Average GDP (in $)", format=",.2f"),
        ],
    )
    .transform_filter(
        (alt.datum.Continent == continent_filtering) | (continent_filtering == "All")
    )
    .add_params(continent_select, continent_filtering)
)


mcv = alt.vconcat(
    alt.hconcat(
        alt.vconcat(
            health_analysis.properties(
                title="Health Analysis: Life Expectancy vs. GDP per Capita; with Physicians per Thousand",
                width=700,
                height=500,
            )
        ).resolve_scale(
            color="independent",
            size="independent",
        ),
        alt.vconcat(
            correlation_chart.properties(
                width=700, height=179, title="Correlation Matrix of Selected Attributes"
            ),
            gdp_bar_chart.properties(
                title="Average GDP per Continent", width=700, height=189
            ),
        ).resolve_scale(
            color="independent",
            size="independent",
        ),
    ).resolve_scale(color="independent", size="independent"),
    alt.hconcat(
        map_graph.properties(
            title="Urbanization: Urban Population (%) vs. Density (P/Km2)",
            width=700,
            height=370,
        ),
        co2_emissions_scatter.properties(
            title="Pollution Contribution related to Economic Power: GDP vs Land Area (Km2); with CO2 Emissions",
            width=700,
            height=365,
        ),
        spacing=85,
    ).resolve_scale(color="independent", size="independent"),
    title=alt.TitleParams(
        text="Analysis of the World Economy and its Impacts",
        subtitle="Click on a country or a continent bar to highlight the selecion or select a continent on the dropdown to filter per continent",
        anchor="middle",
        fontSize=20,
        subtitleFontSize=15,
    ),
)

mcv.save("visualisation.html", format="html")
