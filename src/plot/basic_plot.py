from bokeh.plotting import figure


def plot_result_multi_line(xs_list, ys_list, x_label, y_label, color_list=[], legend_list=[], title=""):
    p = None

    for i in range(len(xs_list)):
        p = plot_result(xs_list[i],
                        ys_list[i],
                        x_label,
                        y_label,
                        color=color_list[i],
                        legend=legend_list[i],
                        title=title,
                        p=p)

    return p


def plot_result(xs, ys, x_label, y_label, color="darkblue", legend=None, title="", p=None):
    xs = [float(x) for x in xs]
    ys = [float(y) for y in ys]

    if not p:
        p = figure(plot_width=500, plot_height=300, title=title, x_axis_label=x_label, y_axis_label=y_label)

    p.line(xs, ys, color=color, alpha=0.8, line_width=2)
    p.circle(xs, ys, color=color, fill_alpha=1, size=4, legend=legend)
    #     p.legend.location = "bottom_right"

    return p