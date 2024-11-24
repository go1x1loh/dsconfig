import os
import argparse
import requests
import xml.etree.ElementTree as ET
from subprocess import run, CalledProcessError
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyAnalyzerError(Exception):
    """Base exception class for DependencyAnalyzer errors."""
    pass

class POMFetchError(DependencyAnalyzerError):
    """Raised when POM file cannot be fetched."""
    pass

class POMParseError(DependencyAnalyzerError):
    """Raised when POM file cannot be parsed."""
    pass

class DependencyAnalyzer:
    """Analyzes Maven package dependencies by fetching and parsing POM files."""
    
    def __init__(self, repo_url: str, max_depth: int):
        """
        Initialize the dependency analyzer.
        
        Args:
            repo_url: Base URL of the Maven repository
            max_depth: Maximum depth of dependency analysis
        """
        self.repo_url = repo_url.rstrip('/')
        self.max_depth = max_depth
        self.dependencies: Dict[str, List[Tuple[str, str, str]]] = {}
        self.processed_packages = set()

    def fetch_pom(self, group_id: str, artifact_id: str, version: str) -> str:
        """
        Fetch POM file from Maven repository.
        
        Args:
            group_id: Maven group ID
            artifact_id: Maven artifact ID
            version: Package version
            
        Returns:
            Content of POM file as string
            
        Raises:
            POMFetchError: If POM file cannot be fetched
        """
        group_path = group_id.replace(".", "/")
        url = f"{self.repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise POMFetchError(f"Failed to fetch POM from {url}: {str(e)}")

    def parse_pom(self, pom_content: str) -> List[Tuple[str, str, str]]:
        """
        Parse POM file content to extract dependencies.
        
        Args:
            pom_content: Content of POM file
            
        Returns:
            List of tuples (group_id, artifact_id, version)
            
        Raises:
            POMParseError: If POM file cannot be parsed
        """
        try:
            root = ET.fromstring(pom_content)
            namespace = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            deps = []
            
            for dep in root.findall('.//mvn:dependency', namespace):
                group_elem = dep.find('mvn:groupId', namespace)
                artifact_elem = dep.find('mvn:artifactId', namespace)
                version_elem = dep.find('mvn:version', namespace)
                
                if None in (group_elem, artifact_elem, version_elem):
                    logger.warning("Skipping incomplete dependency entry")
                    continue
                    
                deps.append((
                    group_elem.text,
                    artifact_elem.text,
                    version_elem.text
                ))
            return deps
        except ET.ParseError as e:
            raise POMParseError(f"Failed to parse POM content: {str(e)}")

    def collect_dependencies(self, group_id: str, artifact_id: str, version: str, depth: int = 0) -> None:
        """
        Recursively collect dependencies for a package.
        
        Args:
            group_id: Maven group ID
            artifact_id: Maven artifact ID
            version: Package version
            depth: Current depth in dependency tree
        """
        if depth > self.max_depth:
            return
            
        package_key = f"{group_id}:{artifact_id}:{version}"
        if package_key in self.processed_packages:
            return
            
        self.processed_packages.add(package_key)
        logger.info(f"Processing dependencies for {package_key} at depth {depth}")
        
        try:
            pom = self.fetch_pom(group_id, artifact_id, version)
            dependencies = self.parse_pom(pom)
            self.dependencies[package_key] = dependencies
            
            for dep in dependencies:
                self.collect_dependencies(*dep, depth + 1)
        except DependencyAnalyzerError as e:
            logger.error(f"Error processing {package_key}: {str(e)}")

class GraphVisualizer:
    """Generates and visualizes dependency graphs using PlantUML."""
    
    def __init__(self, output_path: str):
        """
        Initialize the graph visualizer.
        
        Args:
            output_path: Directory to save output files
        """
        self.output_path = output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)

    def generate_plantuml(self, dependencies: Dict[str, List[Tuple[str, str, str]]]) -> str:
        """
        Generate PlantUML diagram from dependencies.
        
        Args:
            dependencies: Dictionary of package dependencies
            
        Returns:
            PlantUML diagram as string
        """
        lines = [
            "@startuml",
            "skinparam rankdir LR",
            "skinparam component {",
            "  BackgroundColor LightBlue",
            "  BorderColor Black",
            "  ArrowColor Black",
            "}",
            "digraph Dependencies {"
        ]
        
        # Add nodes
        for package in dependencies.keys():
            lines.append(f'  "{package}" [shape=component];')
        
        # Add edges
        for parent, children in dependencies.items():
            for child in children:
                child_key = ":".join(child)
                lines.append(f'  "{parent}" -> "{child_key}";')
        
        lines.extend([
            "}",
            "@enduml"
        ])
        return "\n".join(lines)

    def visualize(self, plantuml_text: str, plantuml_path: str) -> None:
        """
        Generate visual graph using PlantUML.
        
        Args:
            plantuml_text: PlantUML diagram content
            plantuml_path: Path to PlantUML JAR file
            
        Raises:
            RuntimeError: If PlantUML execution fails
        """
        puml_file = os.path.join(self.output_path, "graph.puml")
        png_file = os.path.join(self.output_path, "graph.png")
        
        with open(puml_file, "w") as f:
            f.write(plantuml_text)
            
        try:
            result = run(["java", "-jar", plantuml_path, puml_file], check=True, capture_output=True)
            logger.info(f"Graph saved to {png_file}")
        except (CalledProcessError, OSError) as e:
            error_msg = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.decode('utf-8')
            raise RuntimeError(f"Failed to generate graph: {error_msg}")

def main():
    """Main entry point for the dependency visualizer."""
    parser = argparse.ArgumentParser(
        description="Visualize Maven package dependencies using PlantUML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--repo-url", required=True,
                      help="URL of the Maven repository")
    parser.add_argument("--package", required=True,
                      help="Package to analyze (format: group:artifact:version)")
    parser.add_argument("--depth", type=int, default=3,
                      help="Maximum dependency depth")
    parser.add_argument("--plantuml-path", required=True,
                      help="Path to PlantUML jar file")
    parser.add_argument("--output-path", default=".",
                      help="Output directory for the graph")
    parser.add_argument("--verbose", action="store_true",
                      help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        group, artifact, version = args.package.split(":")
    except ValueError:
        parser.error("Package must be in format 'group:artifact:version'")
        
    try:
        analyzer = DependencyAnalyzer(args.repo_url, args.depth)
        analyzer.collect_dependencies(group, artifact, version)
        
        visualizer = GraphVisualizer(args.output_path)
        plantuml_text = visualizer.generate_plantuml(analyzer.dependencies)
        visualizer.visualize(plantuml_text, args.plantuml_path)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
