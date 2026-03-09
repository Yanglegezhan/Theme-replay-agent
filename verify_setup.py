"""Verify project infrastructure setup."""

import sys
from pathlib import Path


def verify_directories():
    """Verify all required directories exist."""
    project_root = Path(__file__).parent
    
    required_dirs = [
        "config",
        "src/data",
        "src/analysis",
        "src/llm",
        "src/agent",
        "src/output",
        "src/models",
        "src/cli",
        "src/utils",
        "prompts",
        "tests",
        "examples",
        "data/history",
        "output/reports",
        "logs",
    ]
    
    print("Verifying directory structure...")
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} - MISSING")
            all_exist = False
    
    return all_exist


def verify_files():
    """Verify required files exist."""
    project_root = Path(__file__).parent
    
    required_files = [
        "pyproject.toml",
        "README.md",
        "PROJECT_STRUCTURE.md",
        ".gitignore",
        "config/config_manager.py",
        "config/config.example.yaml",
        "src/utils/logger.py",
    ]
    
    print("\nVerifying required files...")
    all_exist = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def verify_imports():
    """Verify basic imports work."""
    print("\nVerifying imports...")
    
    try:
        # Add src to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Test config manager import
        from config.config_manager import ConfigManager
        print("✓ ConfigManager import successful")
        
        # Test logger import
        from src.utils.logger import setup_logger, get_logger
        print("✓ Logger import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def verify_config():
    """Verify configuration system works."""
    print("\nVerifying configuration system...")
    
    try:
        from config.config_manager import ConfigManager
        
        # Load example config
        config = ConfigManager()
        
        # Test basic config access
        llm_config = config.get_llm_config()
        print(f"✓ LLM config loaded: provider={llm_config.get('provider')}")
        
        analysis_config = config.get_analysis_config()
        print(f"✓ Analysis config loaded: {len(analysis_config)} sections")
        
        return True
    except Exception as e:
        print(f"✗ Config verification failed: {e}")
        return False


def verify_logger():
    """Verify logger system works."""
    print("\nVerifying logger system...")
    
    try:
        from src.utils.logger import setup_logger
        
        # Setup logger
        logger = setup_logger(
            name="test_logger",
            level="INFO",
            console_output=True
        )
        
        # Test logging
        logger.info("Test log message")
        print("✓ Logger setup successful")
        
        return True
    except Exception as e:
        print(f"✗ Logger verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Theme Anchor Agent - Infrastructure Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Directory Structure", verify_directories()))
    results.append(("Required Files", verify_files()))
    results.append(("Imports", verify_imports()))
    results.append(("Configuration", verify_config()))
    results.append(("Logger", verify_logger()))
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! Infrastructure is ready.")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
