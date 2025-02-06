import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QComboBox

class CSVSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Search App")
        self.setGeometry(100, 100, 600, 600)
        
        self.df = None
        self.filter_fields = {}
        self.layout = QVBoxLayout()
        
        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_button)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_data)
        self.layout.addWidget(self.search_button)
        
        self.update_label = QLabel("Update Found Items:")
        self.layout.addWidget(self.update_label)
        
        self.update_column_entry = QLineEdit()
        self.update_column_entry.setPlaceholderText("Column to Update")
        self.layout.addWidget(self.update_column_entry)
        
        self.update_value_entry = QLineEdit()
        self.update_value_entry.setPlaceholderText("New Value")
        self.layout.addWidget(self.update_value_entry)
        
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_data)
        self.layout.addWidget(self.update_button)
        
        self.stats_label = QLabel("Select Property to Show Statistics:")
        self.layout.addWidget(self.stats_label)
        
        self.stats_combo = QComboBox()
        self.stats_combo.currentIndexChanged.connect(self.show_statistics)
        self.layout.addWidget(self.stats_combo)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.layout.addWidget(self.stats_text)
        
        self.chart_button = QPushButton("Show Chart")
        self.chart_button.clicked.connect(self.show_chart)
        self.layout.addWidget(self.chart_button)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)
        
        self.setLayout(self.layout)
    
    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                QMessageBox.information(self, "Success", "CSV file loaded successfully!")
                self.create_filter_fields()
                self.populate_stats_combo()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV: {str(e)}")

    def create_filter_fields(self):
        for prop, dtype in self.df.dtypes.items():
            label = QLabel(f"{prop}:")
            self.layout.addWidget(label)
            
            entry = QLineEdit()
            self.layout.addWidget(entry)
            self.filter_fields[prop] = entry
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_label = QLabel(f"Min {prop}:")
                self.layout.addWidget(min_label)
                min_entry = QLineEdit()
                self.layout.addWidget(min_entry)
                self.filter_fields[f"min_{prop}"] = min_entry
                
                max_label = QLabel(f"Max {prop}:")
                self.layout.addWidget(max_label)
                max_entry = QLineEdit()
                self.layout.addWidget(max_entry)
                self.filter_fields[f"max_{prop}"] = max_entry
    
    def search_data(self):
        if self.df is None:
            QMessageBox.critical(self, "Error", "No CSV file loaded.")
            return
        
        conditions = []
        for prop, dtype in self.df.dtypes.items():
            value = self.filter_fields[prop].text().strip()
            if value:
                if pd.api.types.is_numeric_dtype(dtype):
                    try:
                        conditions.append(f"{prop} == {float(value)}")
                    except ValueError:
                        pass
                else:
                    conditions.append(f"{prop}.astype('string').str.contains('{value}', case=False, na=False)")
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_value = self.filter_fields[f"min_{prop}"].text().strip()
                max_value = self.filter_fields[f"max_{prop}"].text().strip()
                
                if min_value:
                    conditions.append(f"{prop} >= {float(min_value)}")
                if max_value:
                    conditions.append(f"{prop} <= {float(max_value)}")
        
        query_string = " & ".join(conditions)
        
        try:
            filtered_df = self.df.query(query_string, engine='python') if conditions else self.df.copy()
            self.result_text.clear()
            self.result_text.setPlainText(filtered_df.to_string(index=False))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Filtering error: {str(e)}")
    
    def update_data(self):
        if self.df is None:
            QMessageBox.critical(self, "Error", "No CSV file loaded.")
            return

        column = self.update_column_entry.text().strip()
        new_value = self.update_value_entry.text().strip()

        if column not in self.df.columns:
            QMessageBox.critical(self, "Error", "Invalid column name.")
            return

        self.df.loc[self.df.index, column] = new_value
        QMessageBox.information(self, "Success", "Values updated successfully!")
        self.search_data()
    
    def populate_stats_combo(self):
        self.stats_combo.clear()
        self.stats_combo.addItems(self.df.columns)
    
    def show_statistics(self):
        if self.df is None:
            return
        
        column = self.stats_combo.currentText()
        if column:
            dtype = self.df[column].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_val = self.df[column].min()
                max_val = self.df[column].max()
                avg_val = self.df[column].mean()
                self.stats_text.setPlainText(f"Min: {min_val}\nMax: {max_val}\nAverage: {avg_val}")
            else:
                unique_values = self.df[column].unique()
                self.stats_text.setPlainText(f"Possible Values:\n" + "\n".join(map(str, unique_values)))
    
    def show_chart(self):
        if self.df is None:
            QMessageBox.critical(self, "Error", "No CSV file loaded.")
            return
        
        numeric_cols = self.df.select_dtypes(include=["number"]).columns
        self.df[numeric_cols].plot(kind='line', figsize=(10, 5), title="Numeric Data Chart")
        plt.xlabel("Index")
        plt.ylabel("Values")
        plt.legend(title="Properties")
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVSearchApp()
    window.show()
    sys.exit(app.exec_())
