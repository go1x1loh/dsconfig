import unittest
from dependency_visualizer import DependencyAnalyzer, GraphVisualizer

class TestDependencyAnalyzer(unittest.TestCase):
    def test_parse_pom(self):
        pom_content = """<project xmlns="http://maven.apache.org/POM/4.0.0">
            <dependencies>
                <dependency>
                    <groupId>org.example</groupId>
                    <artifactId>example-lib</artifactId>
                    <version>1.0.0</version>
                </dependency>
            </dependencies>
        </project>"""
        analyzer = DependencyAnalyzer("http://example.com", 3)
        deps = analyzer.parse_pom(pom_content)
        self.assertEqual(deps, [("org.example", "example-lib", "1.0.0")])

    def test_collect_dependencies(self):
        # Mock network requests and XML parsing
        pass  # Extend this with mocking

class TestGraphVisualizer(unittest.TestCase):
    def test_generate_plantuml(self):
        dependencies = {
            "root": [("org.example", "example-lib", "1.0.0")]
        }
        visualizer = GraphVisualizer(".")
        plantuml = visualizer.generate_plantuml(dependencies)
        self.assertIn('"root" -> "org.example:example-lib:1.0.0";', plantuml)

if __name__ == "__main__":
    unittest.main()

