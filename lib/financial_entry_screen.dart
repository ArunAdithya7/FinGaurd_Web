import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'financial_api.dart';

class FinancialEntryScreen extends StatefulWidget {
  const FinancialEntryScreen({super.key});

  @override
  State<FinancialEntryScreen> createState() => _FinancialEntryScreenState();
}

class _FinancialEntryScreenState extends State<FinancialEntryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final incomeCategoryController = TextEditingController();
  final incomeAmountController = TextEditingController();
  final incomeNotesController = TextEditingController();

  final expenseCategoryController = TextEditingController();
  final expenseAmountController = TextEditingController();
  final expenseNotesController = TextEditingController();

  final debtNameController = TextEditingController();
  final debtOutstandingController = TextEditingController();
  final debtMonthlyPaymentController = TextEditingController();
  final debtInterestController = TextEditingController();

  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    incomeCategoryController.dispose();
    incomeAmountController.dispose();
    incomeNotesController.dispose();
    expenseCategoryController.dispose();
    expenseAmountController.dispose();
    expenseNotesController.dispose();
    debtNameController.dispose();
    debtOutstandingController.dispose();
    debtMonthlyPaymentController.dispose();
    debtInterestController.dispose();
    super.dispose();
  }

  InputDecoration fieldDecoration(String hint, {IconData? icon}) {
    return InputDecoration(
      hintText: hint,
      prefixIcon: icon == null ? null : Icon(icon),
      filled: true,
      fillColor: Colors.white,
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFF2457F5), width: 1.2),
      ),
    );
  }

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token') ?? prefs.getString('token');
  }

  Future<void> _showMessage(String message, {bool isError = false}) async {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : null,
      ),
    );
  }

  Future<void> submitIncome() async {
    final category = incomeCategoryController.text.trim();
    final amountText = incomeAmountController.text.trim();
    final notes = incomeNotesController.text.trim();

    if (category.isEmpty || amountText.isEmpty) {
      _showMessage('Please fill all income fields', isError: true);
      return;
    }

    final amount = double.tryParse(amountText);
    if (amount == null) {
      _showMessage('Enter a valid income amount', isError: true);
      return;
    }

    final token = await _getToken();
    if (token == null || token.isEmpty) {
      _showMessage('Login token not found', isError: true);
      return;
    }

    setState(() => isLoading = true);
    try {
      final result = await FinancialApi.addIncome(
        token: token,
        category: category,
        amount: amount,
        notes: notes.isEmpty ? null : notes,
      );

      _showMessage(result['message'] ?? 'Income saved');
      if (result['success'] == true) {
        incomeCategoryController.clear();
        incomeAmountController.clear();
        incomeNotesController.clear();
      }
    } catch (e) {
      _showMessage(e.toString(), isError: true);
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  Future<void> submitExpense() async {
    final category = expenseCategoryController.text.trim();
    final amountText = expenseAmountController.text.trim();
    final notes = expenseNotesController.text.trim();

    if (category.isEmpty || amountText.isEmpty) {
      _showMessage('Please fill all expense fields', isError: true);
      return;
    }

    final amount = double.tryParse(amountText);
    if (amount == null) {
      _showMessage('Enter a valid expense amount', isError: true);
      return;
    }

    final token = await _getToken();
    if (token == null || token.isEmpty) {
      _showMessage('Login token not found', isError: true);
      return;
    }

    setState(() => isLoading = true);
    try {
      final result = await FinancialApi.addExpense(
        token: token,
        category: category,
        amount: amount,
        notes: notes.isEmpty ? null : notes,
      );

      _showMessage(result['message'] ?? 'Expense saved');
      if (result['success'] == true) {
        expenseCategoryController.clear();
        expenseAmountController.clear();
        expenseNotesController.clear();
      }
    } catch (e) {
      _showMessage(e.toString(), isError: true);
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  Future<void> submitDebt() async {
    final name = debtNameController.text.trim();
    final outstandingText = debtOutstandingController.text.trim();
    final paymentText = debtMonthlyPaymentController.text.trim();
    final interestText = debtInterestController.text.trim();

    if (name.isEmpty || outstandingText.isEmpty || paymentText.isEmpty) {
      _showMessage('Please fill all debt fields', isError: true);
      return;
    }

    final outstanding = double.tryParse(outstandingText);
    final monthlyPayment = double.tryParse(paymentText);
    final interest =
        double.tryParse(interestText.isEmpty ? '0' : interestText) ?? 0.0;

    if (outstanding == null || monthlyPayment == null) {
      _showMessage('Enter valid debt values', isError: true);
      return;
    }

    final token = await _getToken();
    if (token == null || token.isEmpty) {
      _showMessage('Login token not found', isError: true);
      return;
    }

    setState(() => isLoading = true);
    try {
      final result = await FinancialApi.addDebt(
        token: token,
        liabilityName: name,
        outstandingAmount: outstanding,
        monthlyPayment: monthlyPayment,
        interestRate: interest,
      );

      _showMessage(result['message'] ?? 'Debt saved');
      if (result['success'] == true) {
        debtNameController.clear();
        debtOutstandingController.clear();
        debtMonthlyPaymentController.clear();
        debtInterestController.clear();
      }
    } catch (e) {
      _showMessage(e.toString(), isError: true);
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Add Financial Data',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2457F5),
          unselectedLabelColor: Colors.grey,
          indicatorColor: const Color(0xFF2457F5),
          tabs: const [
            Tab(text: 'Income'),
            Tab(text: 'Expense'),
            Tab(text: 'Debt'),
          ],
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _IncomeForm(
                  categoryController: incomeCategoryController,
                  amountController: incomeAmountController,
                  notesController: incomeNotesController,
                  fieldDecoration: fieldDecoration,
                  onSubmit: submitIncome,
                ),
                _ExpenseForm(
                  categoryController: expenseCategoryController,
                  amountController: expenseAmountController,
                  notesController: expenseNotesController,
                  fieldDecoration: fieldDecoration,
                  onSubmit: submitExpense,
                ),
                _DebtForm(
                  nameController: debtNameController,
                  outstandingController: debtOutstandingController,
                  paymentController: debtMonthlyPaymentController,
                  interestController: debtInterestController,
                  fieldDecoration: fieldDecoration,
                  onSubmit: submitDebt,
                ),
              ],
            ),
    );
  }
}

class _IncomeForm extends StatelessWidget {
  final TextEditingController categoryController;
  final TextEditingController amountController;
  final TextEditingController notesController;
  final InputDecoration Function(String hint, {IconData? icon}) fieldDecoration;
  final VoidCallback onSubmit;

  const _IncomeForm({
    required this.categoryController,
    required this.amountController,
    required this.notesController,
    required this.fieldDecoration,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: categoryController,
            decoration: fieldDecoration(
              'Income category',
              icon: Icons.category_outlined,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: amountController,
            keyboardType: TextInputType.number,
            decoration: fieldDecoration('Amount', icon: Icons.currency_rupee),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: notesController,
            maxLines: 3,
            decoration: fieldDecoration('Notes', icon: Icons.notes_outlined),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: onSubmit,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2457F5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Save Income',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ExpenseForm extends StatelessWidget {
  final TextEditingController categoryController;
  final TextEditingController amountController;
  final TextEditingController notesController;
  final InputDecoration Function(String hint, {IconData? icon}) fieldDecoration;
  final VoidCallback onSubmit;

  const _ExpenseForm({
    required this.categoryController,
    required this.amountController,
    required this.notesController,
    required this.fieldDecoration,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: categoryController,
            decoration: fieldDecoration(
              'Expense category',
              icon: Icons.category_outlined,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: amountController,
            keyboardType: TextInputType.number,
            decoration: fieldDecoration('Amount', icon: Icons.currency_rupee),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: notesController,
            maxLines: 3,
            decoration: fieldDecoration('Notes', icon: Icons.notes_outlined),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: onSubmit,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2457F5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Save Expense',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DebtForm extends StatelessWidget {
  final TextEditingController nameController;
  final TextEditingController outstandingController;
  final TextEditingController paymentController;
  final TextEditingController interestController;
  final InputDecoration Function(String hint, {IconData? icon}) fieldDecoration;
  final VoidCallback onSubmit;

  const _DebtForm({
    required this.nameController,
    required this.outstandingController,
    required this.paymentController,
    required this.interestController,
    required this.fieldDecoration,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: nameController,
            decoration: fieldDecoration(
              'Debt name',
              icon: Icons.credit_card_outlined,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: outstandingController,
            keyboardType: TextInputType.number,
            decoration: fieldDecoration(
              'Outstanding amount',
              icon: Icons.currency_rupee,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: paymentController,
            keyboardType: TextInputType.number,
            decoration: fieldDecoration(
              'Monthly payment',
              icon: Icons.payments_outlined,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: interestController,
            keyboardType: TextInputType.number,
            decoration: fieldDecoration(
              'Interest rate (optional)',
              icon: Icons.percent_outlined,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: onSubmit,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2457F5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Save Debt',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
