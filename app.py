import webview
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from arabic_font import get_font_path
html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حاسبة الراتب والنفقات</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #f5f5f5;
            --text-color: #333;
            --background-color: #ffffff;
            --border-radius: 8px;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 20px;
            transition: background-color 0.3s, color 0.3s;
        }
        
        body.dark-mode {
            --primary-color: #64b5f6;
            --secondary-color: #424242;
            --text-color: #e0e0e0;
            --background-color: #212121;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: var(--secondary-color);
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            color: var(--primary-color);
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: var(--border-radius);
            font-size: 16px;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: var(--border-radius);
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        button:hover {
            opacity: 0.9;
        }
        
        #expenseList {
            margin-top: 20px;
        }
        
        .expense-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--secondary-color);
            padding: 10px;
            margin-bottom: 10px;
            border-radius: var(--border-radius);
        }
        
        .expense-item button {
            background-color: #e74c3c;
            padding: 5px 10px;
            font-size: 14px;
        }
        
        .expense-item button:hover {
            background-color: #c0392b;
        }
        
        #result {
            margin-top: 30px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        
        .dark-mode-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
    </style>
</head>
<body>
    <button class="dark-mode-toggle" onclick="toggleDarkMode()">🌓</button>
    <div class="container">
        <h1>حاسبة الراتب والنفقات</h1>
        <div class="input-group">
            <label for="salary">الراتب:</label>
            <input type="number" id="salary" placeholder="أدخل راتبك">
        </div>
        <div class="input-group">
            <label for="period">الفترة:</label>
            <select id="period">
                <option value="monthly">شهري</option>
                <option value="yearly">سنوي</option>
            </select>
        </div>
        <div class="input-group">
            <label for="expenseName">اسم النفقة:</label>
            <input type="text" id="expenseName" placeholder="أدخل اسم النفقة">
        </div>
        <div class="input-group">
            <label for="expenseAmount">مبلغ النفقة:</label>
            <input type="number" id="expenseAmount" placeholder="أدخل مبلغ النفقة">
        </div>
        <div class="input-group">
            <label for="expenseFrequency">تكرار النفقة (مرات في الشهر):</label>
            <input type="number" id="expenseFrequency" placeholder="أدخل عدد مرات تكرار النفقة شهريًا" min="1" value="1">
        </div>
        <button onclick="addExpense()">إضافة نفقة</button>
        <div id="expenseList"></div>
        <button onclick="calculate()">حساب</button>
        <div id="result"></div>
        <button onclick="generatePDF()">تحميل التقرير (PDF)</button>
    </div>

    <script>
        let expenses = [];

        function addExpense() {
            const name = document.getElementById('expenseName').value;
            const amount = parseFloat(document.getElementById('expenseAmount').value);
            const frequency = parseInt(document.getElementById('expenseFrequency').value) || 1;
            
            if (name && amount) {
                expenses.push({ name, amount, frequency });
                updateExpenseList();
                document.getElementById('expenseName').value = '';
                document.getElementById('expenseAmount').value = '';
                document.getElementById('expenseFrequency').value = '1';
            }
        }

        function updateExpenseList() {
            const expenseList = document.getElementById('expenseList');
            expenseList.innerHTML = '';
            
            expenses.forEach((expense, index) => {
                const expenseItem = document.createElement('div');
                expenseItem.className = 'expense-item';
                expenseItem.innerHTML = `
                    <span>${expense.name}: ${expense.amount.toFixed(2)} دج (${expense.frequency} مرة/مرات في الشهر)</span>
                    <button onclick="removeExpense(${index})">حذف</button>
                `;
                expenseList.appendChild(expenseItem);
            });
        }

        function removeExpense(index) {
            expenses.splice(index, 1);
            updateExpenseList();
        }

        function calculate() {
            const salary = parseFloat(document.getElementById('salary').value);
            const period = document.getElementById('period').value;
            const totalExpenses = expenses.reduce((total, expense) => total + (expense.amount * expense.frequency), 0);
            
            let leftover;
            if (period === 'monthly') {
                leftover = salary - totalExpenses;
            } else {
                leftover = (salary * 12) - (totalExpenses * 12);
            }
            
            const resultElement = document.getElementById('result');
            resultElement.textContent = `المبلغ المتبقي ${period === 'monthly' ? 'الشهري' : 'السنوي'}: ${leftover.toFixed(2)} دج`;
        }

        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }

        function generatePDF() {
            const salary = parseFloat(document.getElementById('salary').value);
            const period = document.getElementById('period').value;
            pywebview.api.generate_pdf(salary, period, expenses);
        }
    </script>
</body>
</html>
"""

class Api:
    def generate_pdf(self, salary, period, expenses):
        pdf_path = Path(__file__).parent / "salary_expense_report.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4

        # Register Arabic font
        pdfmetrics.registerFont(TTFont('Arabic', get_font_path()))
        c.setFont('Arabic', 14)

        def draw_arabic_text(text, x, y):
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            c.drawRightString(width - x, height - y, bidi_text)

        # Title
        draw_arabic_text("تقرير الراتب والنفقات", 100, 50)

        # Salary
        draw_arabic_text(f"الراتب {'الشهري' if period == 'monthly' else 'السنوي'}: {salary:.2f} دج", 100, 80)

        # Expenses
        draw_arabic_text("النفقات:", 100, 110)
        y = 130
        total_expenses = 0
        for expense in expenses:
            expense_text = f"{expense['name']}: {expense['amount']:.2f} دج ({expense['frequency']} مرة/مرات في الشهر)"
            draw_arabic_text(expense_text, 120, y)
            total_expenses += expense['amount'] * expense['frequency']
            y += 20

        # Total expenses
        draw_arabic_text(f"إجمالي النفقات: {total_expenses:.2f} دج", 100, y + 20)

        # Leftover
        leftover = salary - total_expenses if period == 'monthly' else (salary * 12) - (total_expenses * 12)
        draw_arabic_text(f"المبلغ المتبقي: {leftover:.2f} دج", 100, y + 40)

        c.save()
        return str(pdf_path)

def save_html_content():
    desktop_path = Path.home() / "Desktop"
    file_path = desktop_path / "salary_expense_calculator.html"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return str(file_path)

if __name__ == "__main__":
    api = Api()
    html_file = save_html_content()
    window = webview.create_window("حاسبة الراتب والنفقات", html_file, width=800, height=800, js_api=api)
    webview.start()