import { Shield } from "lucide-react";
import { Hero } from "../components/home/Hero";
import { ScopeAndApplicability } from "../components/home/ScopeAndApplicability";
import { CoreArchitecture } from "../components/home/CoreArchitecture";
import { EvaluationModules } from "../components/home/EvaluationModules";
import { FiveDimensionComparison } from "../components/home/FiveDimensionComparison";
import { ScoringMethodology } from "../components/home/ScoringMethodology";
import { AdvancedEvidenceProfile } from "../components/home/AdvancedEvidenceProfile";
import { AuditWorkflow } from "../components/home/AuditWorkflow";
import { Results } from "../components/home/Results";
import { LatestChanges } from "../components/home/LatestChanges";
import { McpForAgents } from "../components/home/McpForAgents";
import { Footer } from "../components/home/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/30 selection:text-primary">
      <div className="noise-overlay"></div>

      {/* Top Navbar */}
      <nav className="fixed top-0 left-0 w-full z-40 bg-background/80 backdrop-blur-md border-b border-border/50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono font-bold text-lg">
            <Shield className="text-primary w-5 h-5" />
            <a href="/uhbs-standard/" className="hover:text-primary transition-colors">
              UHBS<span className="text-primary/70 font-light">v4</span>
            </a>
          </div>
          <div className="hidden md:flex items-center gap-6 font-mono text-xs text-secondary-foreground">
            <a href="#scope" className="hover:text-primary transition-colors">Scope</a>
            <a href="#architecture" className="hover:text-primary transition-colors">Architecture</a>
            <a href="#modules" className="hover:text-primary transition-colors">Modules</a>
            <a href="#compare" className="hover:text-primary transition-colors">Compare</a>
            <a href="#scoring" className="hover:text-primary transition-colors">Scoring</a>
            <a href="#results" className="hover:text-primary transition-colors text-primary/80">Results</a>
            <a href="#latest" className="hover:text-primary transition-colors">Latest</a>
            <a href="#mcp" className="hover:text-primary transition-colors">MCP</a>
            <a href="mkdocs/" className="hover:text-primary transition-colors border border-border/60 px-2 py-1">Docs</a>
          </div>
        </div>
      </nav>

      <main>
        <Hero />
        <ScopeAndApplicability />
        <CoreArchitecture />
        <EvaluationModules />
        <FiveDimensionComparison />
        <ScoringMethodology />
        <AdvancedEvidenceProfile />
        <AuditWorkflow />
        <Results />
        <LatestChanges />
        <McpForAgents />
      </main>

      <Footer />
    </div>
  );
}
