import os
import argparse
import requests
import xml.etree.ElementTree as ET
from subprocess import run

class DependencyAnalyzer:
    def __init__(self, repo_url, max_depth):
        self.repo_url = repo_url
        self.max_depth = max_depth
        self.dependencies = {}

    def fetch_pom(self, group_id, artifact_id, version):
        group_path = group_id.replace(".", "/")
        url = f"{self.repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch POM: {url}")
        return response.text

    def parse_pom(self, pom_content):
        root = ET.fromstring(pom_content)
        namespace = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        deps = []
        for dep in root.findall('.//mvn:dependency', namespace):
            group_id = dep.find('mvn:groupId', namespace).text
            artifact_id = dep.find('mvn:artifactId', namespace).text
            version = dep.find('mvn:version', namespace).text
            deps.append((group_id, artifact_id, version))
        return deps

    def collect_dependencies(self, group_id, artifact_id, version, depth=0):
        if depth > self.max_depth:
            return
        key = f"{group_id}:{artifact_id}:{version}"
        if key in self.dependencies:
            return
        try:
            pom = self.fetch_pom(group_id, artifact_id, version)
            dependencies = self.parse_pom(pom)
            self.dependencies[key] = dependencies
            for dep in dependencies:
                self.collect_dependencies(*dep, depth + 1)
        except Exception as e:
            print(f"Error processing {key}: {e}")

class GraphVisualizer:
    def __init__(self, output_path):
        self.output_path = output_path

    def generate_plantuml(self, dependencies):
        lines = ["@startuml", "digraph G {"]
        for parent, children in dependencies.items():
            for child in children:
                lines.append(f'"{parent}" -> "{":".join(child)}";')
        lines.append("}")
        lines.append("@enduml")
        return "\n".join(lines)

    def visualize(self, plantuml_text, plantuml_path):
        puml_file = os.path.join(self.output_path, "graph.puml")
        png_file = os.path.join(self.output_path, "graph.png")
        with open(puml_file, "w") as f:
            f.write(plantuml_text)
        run(["java", "-jar", plantuml_path, puml_file])
        print(f"Graph saved to {png_file}")

def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Visualizer")
    parser.add_argument("--repo-url", required=True, help="URL of the Maven repository")
    parser.add_argument("--package", required=True, help="Package to analyze (format: group:artifact:version)")
    parser.add_argument("--depth", type=int, default=3, help="Maximum dependency depth")
    parser.add_argument("--plantuml-path", required=True, help="Path to PlantUML jar file")
    parser.add_argument("--output-path", default=".", help="Output directory for the graph")
    args = parser.parse_args()

    group, artifact, version = args.package.split(":")
    analyzer = DependencyAnalyzer(args.repo_url, args.depth)
    analyzer.collect_dependencies(group, artifact, version)

    visualizer = GraphVisualizer(args.output_path)
    plantuml_text = visualizer.generate_plantuml(analyzer.dependencies)
    visualizer.visualize(plantuml_text, args.plantuml_path)

if __name__ == "__main__":
    main()

