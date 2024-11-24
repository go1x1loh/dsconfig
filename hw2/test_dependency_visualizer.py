import unittest
from unittest.mock import patch, Mock
import os
import tempfile
import requests
import subprocess
from dependency_visualizer import (
    DependencyAnalyzer, GraphVisualizer,
    POMFetchError, POMParseError
)

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer("http://example.com", 3)
        self.sample_pom = """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencies>
                    <dependency>
                        <groupId>org.example</groupId>
                        <artifactId>example-lib</artifactId>
                        <version>1.0.0</version>
                    </dependency>
                    <dependency>
                        <groupId>org.another</groupId>
                        <artifactId>another-lib</artifactId>
                        <version>2.0.0</version>
                    </dependency>
                </dependencies>
            </project>"""

    def test_parse_pom_with_multiple_dependencies(self):
        """Test parsing POM with multiple dependencies."""
        deps = self.analyzer.parse_pom(self.sample_pom)
        self.assertEqual(len(deps), 2)
        self.assertEqual(deps[0], ("org.example", "example-lib", "1.0.0"))
        self.assertEqual(deps[1], ("org.another", "another-lib", "2.0.0"))

    def test_parse_pom_with_invalid_xml(self):
        """Test parsing invalid POM XML."""
        with self.assertRaises(POMParseError):
            self.analyzer.parse_pom("invalid xml content")

    def test_parse_pom_with_incomplete_dependency(self):
        """Test parsing POM with incomplete dependency information."""
        incomplete_pom = """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencies>
                    <dependency>
                        <groupId>org.example</groupId>
                        <artifactId>example-lib</artifactId>
                    </dependency>
                </dependencies>
            </project>"""
        deps = self.analyzer.parse_pom(incomplete_pom)
        self.assertEqual(len(deps), 0)

    @patch('requests.get')
    def test_fetch_pom_success(self, mock_get):
        """Test successful POM fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_pom
        mock_get.return_value = mock_response

        content = self.analyzer.fetch_pom("org.example", "example-lib", "1.0.0")
        self.assertEqual(content, self.sample_pom)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_pom_failure(self, mock_get):
        """Test POM fetch failure."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(POMFetchError):
            self.analyzer.fetch_pom("org.example", "example-lib", "1.0.0")

    @patch('dependency_visualizer.DependencyAnalyzer.fetch_pom')
    @patch('dependency_visualizer.DependencyAnalyzer.parse_pom')
    def test_collect_dependencies(self, mock_parse_pom, mock_fetch_pom):
        """Test dependency collection."""
        mock_fetch_pom.return_value = self.sample_pom
        mock_parse_pom.return_value = [
            ("org.example", "lib1", "1.0.0"),
            ("org.example", "lib2", "1.0.0")
        ]

        self.analyzer.collect_dependencies("org.root", "root-lib", "1.0.0")
        
        # Check that root package was processed
        root_key = "org.root:root-lib:1.0.0"
        self.assertIn(root_key, self.analyzer.dependencies)
        
        # Check that dependencies were collected
        self.assertEqual(len(self.analyzer.dependencies[root_key]), 2)
        
        # Check depth limit
        self.assertLessEqual(len(self.analyzer.processed_packages), self.analyzer.max_depth + 1)

class TestGraphVisualizer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = GraphVisualizer(self.temp_dir)
        self.dependencies = {
            "org.example:root:1.0.0": [
                ("org.example", "lib1", "1.0.0"),
                ("org.example", "lib2", "1.0.0")
            ],
            "org.example:lib1:1.0.0": [
                ("org.example", "lib3", "1.0.0")
            ]
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_generate_plantuml(self):
        """Test PlantUML diagram generation."""
        plantuml = self.visualizer.generate_plantuml(self.dependencies)
        
        # Check basic structure
        self.assertIn("@startuml", plantuml)
        self.assertIn("@enduml", plantuml)
        self.assertIn("digraph Dependencies", plantuml)
        
        # Check styling
        self.assertIn("skinparam", plantuml)
        self.assertIn("BackgroundColor", plantuml)
        
        # Check nodes and edges
        self.assertIn('"org.example:root:1.0.0"', plantuml)
        self.assertIn('"org.example:lib1:1.0.0"', plantuml)
        self.assertIn(' -> ', plantuml)

    @patch('subprocess.run')
    def test_visualize_success(self, mock_run):
        """Test successful graph visualization."""
        # Configure mock to simulate successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b"PlantUML success",
            stderr=b""
        )
        mock_run.side_effect = None
        
        plantuml = self.visualizer.generate_plantuml(self.dependencies)
        self.visualizer.visualize(plantuml, "plantuml.jar")
        
        # Check that PlantUML file was created
        puml_file = os.path.join(self.temp_dir, "graph.puml")
        self.assertTrue(os.path.exists(puml_file))
        
        # Check PlantUML was called with correct arguments
        mock_run.assert_called_once_with(
            ["java", "-jar", "plantuml.jar", puml_file],
            check=True,
            capture_output=True
        )

    @patch('subprocess.run')
    def test_visualize_failure(self, mock_run):
        """Test graph visualization failure."""
        # Configure mock to simulate PlantUML failure
        error_msg = "PlantUML error: Invalid syntax"
        mock_run.return_value = None
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["java", "-jar", "plantuml.jar"],
            output=b"",
            stderr=error_msg.encode()
        )
        
        plantuml = self.visualizer.generate_plantuml(self.dependencies)
        with self.assertRaises(RuntimeError) as ctx:
            self.visualizer.visualize(plantuml, "plantuml.jar")
        self.assertIn(error_msg, str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
