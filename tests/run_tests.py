import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from test_ast_scanner import test_ast_scanner_openai_and_sqlite, test_ast_scanner_dangerous_shell
from test_compliance_engine import (
    test_evaluate_compliance_completeness_full,
    test_evaluate_compliance_completeness_with_placeholder,
    test_risk_formula_calculation
)


def main():
    print("=" * 60)
    print(" Running AgentGuard AI Native Unit Test Suite...")
    print("=" * 60)

    # 1. Test AST static code scanner
    test_ast_scanner_openai_and_sqlite()
    print(" [PASS] test_ast_scanner_openai_and_sqlite")

    test_ast_scanner_dangerous_shell()
    print(" [PASS] test_ast_scanner_dangerous_shell")

    # 2. Test Compliance Card Completeness Engine & Risk Calculations
    test_evaluate_compliance_completeness_full()
    print(" [PASS] test_evaluate_compliance_completeness_full")

    test_evaluate_compliance_completeness_with_placeholder()
    print(" [PASS] test_evaluate_compliance_completeness_with_placeholder")

    test_risk_formula_calculation()
    print(" [PASS] test_risk_formula_calculation")

    print("=" * 60)
    print(" SUCCESS: All 5 core unit tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
