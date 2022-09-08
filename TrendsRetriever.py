import sys
import os

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QApplication,
    QVBoxLayout,
    QPushButton,
)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# for querying data
from pytrends.request import TrendReq

# for plotting data

# path of project
bundle_dir = os.path.dirname(__file__)


# used to embed plot into pyqt
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Trends Data")

        # selected topic
        self.user_choice = ['bitcoin']
        # selected daily data (e.g. 'today 5-y', 'today 1-m', 'now 3-d')
        self.user_timeframe = '2015-01-01 2022-09-08'
        # timeframe defines length of time


        # Create the matplotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.sc = MplCanvas(self, width=12, height=12, dpi=60)

        # 360 is google's value for CST/MST
        self.pytrends = TrendReq(hl='en-US', tz=360)

        self.pytrends.build_payload(self.user_choice, cat=0,
                                    timeframe=self.user_timeframe,
                                    geo='',
                                    gprop='')

        # now create basic menu to select all the most common options

        data_controls = QWidget()
        input_layout = QVBoxLayout()

        input_layout.addWidget(QLabel("Selected topic: " + self.user_choice[0]))

        self.action_type = [QPushButton("Interest over time"),
                            QPushButton("Interest by region"),
                            QPushButton("Related Topics"),
                            QPushButton("Related Queries")]

        # add functionality to buttons
        self.action_type[0].clicked.connect(self.connect_interest_over_time)
        self.action_type[1].clicked.connect(self.connect_interest_by_region)
        self.action_type[2].clicked.connect(self.connect_topics)
        self.action_type[3].clicked.connect(self.connect_queries)

        for item in self.action_type:
            input_layout.addWidget(item)

        data_controls.setLayout(input_layout)
        self.setCentralWidget(data_controls)
        self.show()

    def connect_interest_over_time(self):
        self.display_interest_ot()

    def connect_interest_by_region(self):
        self.display_interest_br(self.user_choice, 'COUNTRY')

    def connect_topics(self):
        self.display_topics()

    def connect_queries(self):
        self.display_queries()

    def display_interest_ot(self):
        # create module to display our interest over time info
        self.hide()


        # save into pandas dataframe for further usage
        info_ot = self.pytrends.interest_over_time()

        # write dataframe to file, only works with windows for now
        # can be optional, could make function for ease of use
        print(bundle_dir)
        info_ot.to_csv(bundle_dir + "\\interest_ot.csv")

        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        info_ot.plot(ax=self.sc.axes)

        toolbar = NavigationToolbar(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def display_interest_br(self, topic, location):
        # create module to display our interest by region info
        self.hide()

        top_results = 5
        info_br = self.pytrends.interest_by_region(resolution=location,
                                                   inc_low_vol=True,
                                                   inc_geo_code=False).nlargest(
            top_results,
            topic)


        print(info_br)

        info_br.plot.bar(ax=self.sc.axes)


        toolbar = NavigationToolbar(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def display_topics(self):
        # module for topics
        self.hide()
        topics = self.pytrends.related_topics()[self.user_choice[0]][
            'rising']  # .set_index('topic_title')


        # drop unneeded columns and combine type/title into one
        topics['topic_title'] = topics['topic_title'] + ' ' + topics[
            'topic_type']
        topics.drop(['formattedValue', 'link', 'topic_mid', 'topic_type'],
                    axis=1, inplace=True)

        topics = topics.set_index('topic_title')

        print(topics)


        topics.plot.pie(ax=self.sc.axes, subplots=True)
        toolbar = NavigationToolbar(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()

    def display_queries(self):
        # module for queries
        self.hide()
        queries = self.pytrends.related_queries()[self.user_choice[0]][
            'rising'].set_index('query')


        print(queries)

        queries.plot.pie(ax=self.sc.axes, subplots=True)
        toolbar = NavigationToolbar(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
