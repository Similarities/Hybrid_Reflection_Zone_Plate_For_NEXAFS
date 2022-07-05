import matplotlib.pyplot as plt
import basic_file_app
import plot_filter2


class BatchFilter:
    def __init__(self, path):

        self.path = path
        self.file_list = self.get_file_list()


    def get_file_list(self):
        return basic_file_app.get_file_list(self.path)

    def plot_all_filters(self):
        for x in self.file_list:
            filter = plot_filter2.PlotFilter(x, self.path, "eV", 1)
            filter.plot_filter_data()
        plt.savefig(str(self.path) + ".png", bbox_inches="tight", dpi=500)


    def plot_resulting_transmission(self):
        filter = plot_filter2.PlotFilter(self.file_list[0], self.path, "eV", 2)
        for x in self.file_list[1:]:
            filter.add_filter_calc_transparency(x)
        filter.plot_filter_data()
        filter.plot_second_order()
        plt.yscale("log")
        plt.ylim(0.5E-1, 0.6)
        plt.savefig(str(self.path) + "resulting_"+ ".png", bbox_inches="tight", dpi=500)




path = "filter/sandwich_mix1"
sandwich30nm = BatchFilter(path)
sandwich30nm.plot_resulting_transmission()
plt.show()




