import { Shield } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="py-12 border-t-2 border-border bg-secondary-background">
      <div className="container mx-auto px-6 text-center">
        <div className="flex justify-center items-center gap-2 mb-6 text-main">
          <Shield className="w-6 h-6" aria-hidden />
        </div>
        <div className="font-mono text-sm text-muted-foreground mb-4">
          Universal Honeypot Benchmarking Standard <span className="text-main">·</span> v4.6.0{" "}
          <span className="text-main">·</span> 2026
        </div>
        <p className="text-xs text-muted-foreground max-w-lg mx-auto mb-6">
          Open-source evaluation framework (Apache-2.0). Not a consortium, Steering Committee, or
          adopted industry standard.
        </p>
        <div className="flex flex-wrap justify-center gap-6 font-mono text-xs text-muted-foreground">
          <a href="mkdocs/" className="hover:text-foreground transition-colors">
            Docs
          </a>
          <a href="#latest" className="hover:text-foreground transition-colors">
            Latest
          </a>
          <a href="#results" className="hover:text-foreground transition-colors">
            Results
          </a>
          <a href="#mcp" className="hover:text-foreground transition-colors">
            MCP
          </a>
          <a
            href="https://github.com/uhbs/uhbs-standard/blob/main/CHANGELOG.md"
            className="hover:text-foreground transition-colors"
          >
            Changelog
          </a>
          <a href="mkdocs/scorecards/" className="hover:text-foreground transition-colors">
            Scorecards
          </a>
          <a href="mkdocs/conformance/reports/" className="hover:text-foreground transition-colors">
            Lab reports
          </a>
          <a
            href="https://github.com/uhbs/uhbs-standard"
            className="hover:text-foreground transition-colors"
          >
            GitHub
          </a>
          <a href="llms.txt" className="hover:text-foreground transition-colors">
            llms.txt
          </a>
          <a href="llms-full.txt" className="hover:text-foreground transition-colors">
            llms-full.txt
          </a>
          <a href="sitemap.xml" className="hover:text-foreground transition-colors">
            sitemap
          </a>
          <a href=".well-known/security.txt" className="hover:text-foreground transition-colors">
            security.txt
          </a>
          <a href="#scoring" className="hover:text-foreground transition-colors">
            UHQS &gt; 80 gate
          </a>
        </div>
      </div>
    </footer>
  );
};
