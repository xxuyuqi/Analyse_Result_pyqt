import sys
import os.path
import numpy as np
import h5py
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox, QButtonGroup
from PyQt5 import QtCore, QtGui
from mainwindow import Ui_Form
from plot_fun import Plotfun


class MainWin(QWidget, Ui_Form):
    def __init__(self, app) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.app = app
        self.setupUi(self)
        self.qbg = QButtonGroup()
        self.qbg.addButton(self.radioButton, 0)
        self.qbg.addButton(self.radioButton_2, 1)
        self.qbg.addButton(self.radioButton_3, 2)
        self.setWindowTitle("Result")
        self.hdf = None
        self.para = np.loadtxt('config.ini', delimiter=',') if os.path.isfile("config.ini") else (6.0, 1000.0, 1.0) # x, f, r
        self.lineEdit_3.setText(str(self.para[0]))
        self.lineEdit_4.setText(str(self.para[1]))
        self.lineEdit_5.setText(str(self.para[2]))
        self.connect_slot()

    def data_open(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'QFileDialog.getOpenFileName()',
            'D:\\data',
            'HDF5 Files (*.hdf *.h5 *.hdf5)',
            options=options
        )

        if filename:
            self.open_file(filename)

    def open_file(self, filename):
        """
        Open a hdf5 file
        """
        try:
            hdf = h5py.File(filename, 'r')
        except OSError as e:
            hdf = None
            QMessageBox.critical(
                self,
                'File loading error',
                '<p>{}</p><p>{}</p>'.format(e, filename)
            )
        if hdf:
            if self.hdf:
                self.hdf.close()
            self.hdf = hdf
            self.label.setText(self.hdf.filename)
            self.pushButton_2.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            message = '<p>' + hdf['/log'][0].decode() + '</p>'
            QMessageBox.information(self, "parameter", message)
    
    def close_file(self):
        if self.hdf:
            self.hdf.close()
        self.label.setText('')
        
    
    def para_edit(self):
        self.para = [float(self.lineEdit_3.text()), float(self.lineEdit_4.text()), float(self.lineEdit_5.text())]

    def plot_best(self):
        reply = QMessageBox.question(None, "Message", "You sure to plot?", QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.No:
            return
        if self.checkBox.isChecked():
            bi = self.best_data(-1)
        else:
            for i in range(self.hdf['/bestInd/chrom'].shape[0]):
                bi = self.best_data(i)
        bi = bi.split('-')
        self.spinBox.setValue(int(bi[1]))
        self.spinBox_2.setValue(int(bi[3]))
    
    
    def best_data(self, i):
        arrData = self.hdf["/bestInd/chrom"][i, :, :]
        name = self.hdf["/bestInd/name"][i].decode().strip()
        loc = '/evoData/' + name.split('-i')[0] + '/' + name
        try:
            lcData = self.hdf[loc]
        except:
            lcData = None
        if not lcData or self.qbg.checkedId()==1:
            Plotfun.plot_pop(arrData)
        elif self.qbg.checkedId()==0:
            Plotfun.plot_union(arrData, lcData, self.para)
        else:
            Plotfun.plot_curve(lcData, self.para)
        Plotfun.show()
        return name

    def save_data(self):
        gen = self.spinBox.value()
        ind = self.spinBox_2.value()
        if gen == 0 or ind == 0:
            QMessageBox.critical(
                self,
                'No data error',
                '<p>data doesn\'t exist!</p>')
            return
        gdir = f"G-{gen}"
        indname = f"G-{gen}-ind-{ind}"
        chromloc = "/".join(["/evoData", gdir, "chrom"])
        lc_loc = "/".join(["/evoData", gdir, indname])
        fn = "D:\\"+indname
        if self.qbg.checkedId() != 2:
            chrom = self.hdf[chromloc][ind-1, :, :]
            np.savetxt(fn+"_struc.csv", chrom, fmt="%d", delimiter=',')
        else:
            chrom = None
        try:
            lcData = self.hdf[lc_loc]
        except:
            lcData = None
        if lcData and self.qbg.checkedId()!=1:
            np.savetxt(fn+"_lc.csv", lcData, fmt="%.6f", delimiter=',')
        if chrom is not None:
            QMessageBox.information(self, "Infromation", f"Files saved successfully, Solid occupancy : {(np.sum(chrom)+400)/28:.4}%")

    def plot(self):
        gen = self.spinBox.value()
        ind = self.spinBox_2.value()
        if gen == 0:
            QMessageBox.critical(
                self,
                'Generation error',
                '<p>Generation=0!</p>')
            return
        if ind == 0:
            for i in range(self.hdf['/evoData/G-1/chrom'].shape[0]):
                self.handle_plot(gen, i+1)
        else:
            self.handle_plot(gen, ind)
    
    def handle_plot(self, gen, ind):
        gdir = f"G-{gen}"
        indname = f"G-{gen}-ind-{ind}"
        chromloc = "/".join(["/evoData", gdir, "chrom"])
        lc_loc = "/".join(["/evoData", gdir, indname])
        chrom = self.hdf[chromloc][ind-1, :, :]
        if self.qbg.checkedId()==1:
            Plotfun.plot_pop(chrom)
            Plotfun.show()
            return
        try:
            lcData = self.hdf[lc_loc]
        except:
            lcData = None
        if not lcData:
            return
        if self.qbg.checkedId()==0:
            Plotfun.plot_union(chrom, lcData, self.para)
        else:
            Plotfun.plot_curve(lcData, self.para)
        Plotfun.show()

    def next_dir(self):
        self.spinBox.stepUp()
        self.plot()
    
    def get_dropped_file(self, event : QtGui.QDragEnterEvent):
        return event.mimeData().urls()[-1].toLocalFile()


    # Event
    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        a0.accept() if self.get_dropped_file(a0) else a0.ignore
    

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        self.open_file(self.get_dropped_file(a0))
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_file()
        np.savetxt("config.ini", self.para, fmt='%f')
        self.app.exit()
        a0.accept()


    def connect_slot(self):
        self.pushButton.clicked.connect(self.data_open)
        self.pushButton_10.released.connect(self.close_file)
        for qo in (self.lineEdit_3, self.lineEdit_4, self.lineEdit_5):
            qo.editingFinished.connect(self.para_edit)
        self.pushButton_2.clicked.connect(self.plot_best)
        self.pushButton_4.clicked.connect(self.save_data)
        self.pushButton_5.clicked.connect(self.plot)
        self.pushButton_9.released.connect(Plotfun.close_all)
        self.pushButton_3.clicked.connect(self.next_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWin(app) # 必须赋值，不然python会回收这个对象
    mw.show()
    sys.exit(app.exec_())
