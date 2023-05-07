import sys

from PyQt5.QtChart import QChartView, QBarSeries, QBarSet, QChart, QPieSeries
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
import mysql.connector


class Example(QWidget):

    def __init__(self, slef=None):
        super().__init__()

        # MariaDB 연결 정보 입력
        self.mydb = mysql.connector.connect(
            host="10.10.141.61",
            user="root",
            password="0000",
            database="mysql"
        )

        # 폰트 크기

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chart.setTitle("Fish Count")

        # 원형 차트 데이터를 추가
        self.pieseries = QPieSeries()
        self.pieseries.append("Pterophyllum", self.get_count('Pterophyllum'))
        self.pieseries.append("ikan-mas", self.get_count('ikan-mas'))
        self.pieseries.append("Arapaima gigas", self.get_count('Arapaima gigas'))

        # 차트를 차트 뷰에 추가
        self.chart.addSeries(self.pieseries)
        self.chart.createDefaultAxes()

        # 화면 출력
        self.ochartview = QChartView(self.chart, self)

        # 바 차트를 생성
        self.chart = QChart()
        self.chart.setTitle("Fish Count")

        # 바 차트 데이터를 추가
        self.barset = QBarSet("Fish Species")
        self.barset.append([self.get_count('Pterophyllum'),
                            self.get_count('ikan-mas'),
                            self.get_count('Arapaima gigas')])
        self.series = QBarSeries()
        self.series.append(self.barset)

        # 차트를 차트 뷰에 추가
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.axisX().setTitleText("Fish Species")
        self.chart.axisY().setTitleText("Count")
        self.chart.axisY().setRange(0, 10)

        #화면 출력
        self.chartview = QChartView(self.chart, self)

        # QLabels 생성
        self.ptero_label = QLabel(f"Pterophyllum: {self.get_count('Pterophyllum')}", self)
        self.carp_label = QLabel(f"ikan-mas: {self.get_count('ikan-mas')}", self)
        self.arap_label = QLabel(f"Arapaima gigas: {self.get_count('Arapaima gigas')}", self)
        self.btn_clear = QPushButton('Clear Table', self)
        self.btn_clear.clicked.connect(self.clear_table)

        # QLabels 위치 설정
        self.layout = QVBoxLayout(self)
        self.layout1 = QHBoxLayout(self)
        self.layout2 = QHBoxLayout(self)

        # 가로
        self.layout1.addWidget(self.ptero_label)
        self.layout1.addWidget(self.carp_label)
        self.layout1.addWidget(self.arap_label)

        # 세로
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.btn_clear)

        # 2번째 세로
        self.layout2.addWidget(self.ochartview)
        self.layout2.addWidget(self.chartview)


        # 각 라벨의 스타일시트를 기술합니다.
        self.ptero_label.setStyleSheet("background-color: #EDEDED; border-radius: 10%; padding: 10px;")
        self.carp_label.setStyleSheet("background-color: #EDEDED; border-radius: 10%; padding: 10px;")
        self.arap_label.setStyleSheet("background-color: #EDEDED; border-radius: 10%; padding: 10px;")
        self.setStyleSheet("background-color: #D9E5FF; border-radius: 10%;")
        self.btn_clear.setStyleSheet("background-color: #EDEDED; border-radius: 10%; padding: 10px;")

        # 각 라벨의 너비를 150으로 설정
        self.ptero_label.setFixedWidth(210)
        self.carp_label.setFixedWidth(210)
        self.arap_label.setFixedWidth(250)
        self.btn_clear.setFixedWidth(800)

        #폰트 설정
        font = self.arap_label.font()
        font = self.carp_label.font()
        font = self.ptero_label.font()
        font.setFamily('Arial')
        font.setBold(True)
        self.ptero_label.setFont(font)
        self.carp_label.setFont(font)
        self.arap_label.setFont(font)


        # 타이머 생성 및 연결
        self.mytimer = QTimer()
        self.mytimer.timeout.connect(self.update_counts)
        self.mytimer.start(500)


        self.setGeometry(800, 800, 450, 450)
        self.setWindowTitle('Fish Count')



    def update_counts(self):
        # MariaDB 연결 정보 입력 재접속
        self.mydb = mysql.connector.connect(
            host="10.10.141.61",
            user="root",
            password="0000",
            database="mysql"
        )
        #다른 값이 들어왔을때 그 값을 삭제.
        if self.get_count("Pterophyllum") != 0:
            Error = QMessageBox.critical(self, 'Error', 'Wrong value entered !')
            QMessageBox.critical(self, 'Message', 'Are you sure to delete the data?')
            self.delete("Pterophyllum")


            # QLabel의 텍스트 업데이트
        self.ptero_label.setText(f"Pterophyllum: {self.get_count('Pterophyllum')}")
        self.carp_label.setText(f"ikan-mas: {self.get_count('ikan-mas')}")
        self.arap_label.setText(f"Arapaima gigas: {self.get_count('Arapaima gigas')}")

        self.barset = QBarSet("Fish Species")
        self.barset.append([self.get_count('Pterophyllum'),
                            self.get_count('ikan-mas'),
                            self.get_count('Arapaima gigas')])

        self.series.clear()
        self.series.append(self.barset)
        # QPieSeries 업데이트
        self.pieseries.clear()
        self.pieseries.append("Pterophyllum", self.get_count('Pterophyllum'))
        self.pieseries.append("ikan-mas", self.get_count('ikan-mas'))
        self.pieseries.append("Arapaima gigas", self.get_count('Arapaima gigas'))


    def get_count(self, name):
        # MariaDB에서 해당 객체의 개수 가져오기
        mycursor = self.mydb.cursor()
        mycursor.execute(f"SELECT COUNT(*) FROM fish WHERE name = '{name}'")
        row = mycursor.fetchone()
        if row:
            result = row[0]
        return result

    def delete(self, name):
        # 다른 값(종류)가 들어왔을때 삭제처리
        cursor = self.mydb.cursor()
        cursor.execute(f"DELETE FROM fish WHERE name ='{name}'")
        self.mydb.commit()
        QMessageBox.information(self, 'Success', 'Data deleted successfully!')

    def clear_table(self):
        # 테이블안에 있는 데이터 all clear
        mycursor = self.mydb.cursor()
        sql = "DELETE FROM fish"
        mycursor.execute(sql)
        self.mydb.commit()
        QMessageBox.information(self, "Success", "Table cleared successfully.")

    #윈도우 창
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())