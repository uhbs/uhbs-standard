import { motion } from "framer-motion";
import { fadeUpVariant, staggerContainer } from "./motion";

export const AuditWorkflow = () => {
  const steps = [
    { num: 1, title: "Profile Setup", desc: "Define Target Profile Specification (TPS)" },
    { num: 2, title: "Static Audit", desc: "Execute Module F White-Box Scans" },
    { num: 3, title: "Provisioning", desc: "Deploy Sandbox & Gold Baseline" },
    { num: 4, title: "Live Execution", desc: "Adversarial Probing (Modules A-E)" },
    { num: 5, title: "Computation", desc: "Compute UHQS & Final Report" }
  ];

  return (
    <section className="py-24 border-t border-border/50 bg-[#0f1629]/50">
      <motion.div 
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.h2 variants={fadeUpVariant} className="text-3xl font-bold font-sans mb-12 text-center">Standard Audit Workflow</motion.h2>
        
        <div className="relative">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-1/2 left-0 w-full h-px bg-border -translate-y-1/2 z-0"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 relative z-10">
            {steps.map((step, i) => (
              <motion.div key={i} variants={fadeUpVariant} className="flex flex-row md:flex-col items-center md:text-center gap-4 group">
                <div className="w-12 h-12 rounded-full bg-background border-2 border-border flex items-center justify-center font-mono text-lg font-bold group-hover:border-primary transition-colors shrink-0">
                  {step.num}
                </div>
                <div>
                  <h4 className="font-bold text-foreground text-sm mb-1">{step.title}</h4>
                  <p className="text-xs font-mono text-muted-foreground">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
};

// Section 7: Results — published tutorials, runs, scorecards
