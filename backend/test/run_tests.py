"""
Test runner for py2048 backend tests
Run this script to execute all tests or specific test suites
"""

import unittest
import sys
import os

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Import all test modules
    from test_game_basic import TestGameBasic, TestGameValidation
    from test_move_logic import TestMoveLogic, TestMergeStrategies, TestGameEndConditions
    from test_advanced_features import (TestStreakSystem, TestRedoFunctionality, 
                                      TestHintSystem, TestRandomTileGeneration, 
                                      TestDisplayAndAPI)
    from test_integration import TestGameIntegration, TestCommandProcessing, TestEdgeCases
    
    # Add all test classes
    test_classes = [
        TestGameBasic,
        TestGameValidation,
        TestMoveLogic,
        TestMergeStrategies,
        TestGameEndConditions,
        TestStreakSystem,
        TestRedoFunctionality,
        TestHintSystem,
        TestRandomTileGeneration,
        TestDisplayAndAPI,
        TestGameIntegration,
        TestCommandProcessing,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite

def run_specific_test(test_name):
    """Run a specific test suite"""
    loader = unittest.TestLoader()
    
    try:
        if test_name == 'basic':
            from test_game_basic import TestGameBasic, TestGameValidation
            suite = unittest.TestSuite()
            suite.addTests(loader.loadTestsFromTestCase(TestGameBasic))
            suite.addTests(loader.loadTestsFromTestCase(TestGameValidation))
        elif test_name == 'move':
            from test_move_logic import TestMoveLogic, TestMergeStrategies, TestGameEndConditions
            suite = unittest.TestSuite()
            suite.addTests(loader.loadTestsFromTestCase(TestMoveLogic))
            suite.addTests(loader.loadTestsFromTestCase(TestMergeStrategies))
            suite.addTests(loader.loadTestsFromTestCase(TestGameEndConditions))
        elif test_name == 'advanced':
            from test_advanced_features import (TestStreakSystem, TestRedoFunctionality, 
                                              TestHintSystem, TestRandomTileGeneration, 
                                              TestDisplayAndAPI)
            suite = unittest.TestSuite()
            suite.addTests(loader.loadTestsFromTestCase(TestStreakSystem))
            suite.addTests(loader.loadTestsFromTestCase(TestRedoFunctionality))
            suite.addTests(loader.loadTestsFromTestCase(TestHintSystem))
            suite.addTests(loader.loadTestsFromTestCase(TestRandomTileGeneration))
            suite.addTests(loader.loadTestsFromTestCase(TestDisplayAndAPI))
        elif test_name == 'integration':
            from test_integration import TestGameIntegration, TestCommandProcessing, TestEdgeCases
            suite = unittest.TestSuite()
            suite.addTests(loader.loadTestsFromTestCase(TestGameIntegration))
            suite.addTests(loader.loadTestsFromTestCase(TestCommandProcessing))
            suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
        else:
            print(f"Unknown test suite: {test_name}")
            print("Available test suites: basic, move, advanced, integration")
            return None
        
        return suite
    except ImportError as e:
        print(f"Error importing test module: {e}")
        return None

def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run py2048 backend tests')
    parser.add_argument('--suite', '-s', type=str, help='Specific test suite to run (basic, move, advanced, integration)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose test output')
    
    args = parser.parse_args()
    
    # Configure test runner
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    print("🎮 Running py2048 Backend Tests")
    print("=" * 50)
    
    # Determine which tests to run
    if args.suite:
        print(f"Running test suite: {args.suite}")
        suite = run_specific_test(args.suite)
        if suite is None:
            return 1
    else:
        print("Running all tests")
        suite = run_all_tests()
    
    # Run the tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏆 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
