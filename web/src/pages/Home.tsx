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

const NAV = [
  { href: "#scope", label: "Scope" },
  { href: "#architecture", label: "Architecture" },
  { href: "#modules", label: "Modules" },
  { href: "#compare", label: "Compare" },
  { href: "#scoring", label: "Scoring" },
  { href: "#results", label: "Results" },
  { href: "#latest", label: "Latest" },
  { href: "#mcp", label: "MCP" },
] as const;

export default function Home() {
  return (
    <div className="min-h-screen bg-page text-foreground font-sans selection:bg-main selection:text-black">
      <nav className="fixed top-0 left-0 w-full z-40 bg-secondary-background border-b-2 border-border shadow-shadow">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <a
            href="/uhbs-standard/"
            className="flex items-center gap-2 font-mono font-heading text-lg text-foreground hover:text-main transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2"
          >
            <Shield className="text-main w-5 h-5" aria-hidden />
            UHBS<span className="text-muted-foreground font-base">v4</span>
          </a>
          <div className="hidden md:flex items-center gap-5 font-mono text-xs text-muted-foreground">
            {NAV.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="hover:text-foreground transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2"
              >
                {item.label}
              </a>
            ))}
            <a
              href="mkdocs/"
              className="border-2 border-border bg-main text-black px-2.5 py-1 shadow-shadow hover:translate-x-boxShadowX hover:translate-y-boxShadowY hover:shadow-none transition-all"
            >
              Docs
            </a>
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
