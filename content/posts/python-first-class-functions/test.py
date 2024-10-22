import streamlit as st
import plotly.express as px

data = {
    'time': [0.1, 0.2, 0.3, 0.4, 0.5],
    'value': [10, -10, 20, -20, 30]
}


options_list = [px.scatter, px.line, px.bar]

list_plot_type = st.selectbox("list plot type", options_list)

list_fig = list_plot_type(data, x="time", y="value", title="list plot")
st.plotly_chart(list_fig)


options_dict = {"scatter": px.scatter, "line": px.line, "bar": px.bar}

dict_plot_type = st.selectbox("dict plot type", options_dict.keys(), index=list(options_dict.keys()).index("line"))

dict_fig = options_dict[dict_plot_type](data, x="time", y="value", title="dict plot")
st.plotly_chart(dict_fig)


attr_options = ["scatter", "line", "bar"]
attr_plot_type = st.selectbox("attr plot type", options=attr_options, index=attr_options.index("bar"))
px_plot = getattr(px, attr_plot_type)

# fig = px.bar(data, x="time", y="value") # normally we'd plot like this
attr_fig = px_plot(data, x="time", y="value")   # with getattr() we plot like this
st.plotly_chart(attr_fig)
