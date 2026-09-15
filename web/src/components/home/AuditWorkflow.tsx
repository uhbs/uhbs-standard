import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const AuditWorkflow = () => {
  const steps = [
    { num: 1, title: "Profile Setup", desc: "Define Target Profile Specification (TPS)" },
    { num: 2, title: "Static Audit", desc: "Execute Module F White-Box Scans" },
    { num: 3, title: "Provisioning", desc: "Deploy Sandbox & Gold Baseline" },
    { num: 4, title: "Live Execution", desc: "Adversarial Probing (Modules A-E)" },
    { num: 5, title: "Computation", desc: "Compute UHQS & Final Report" },
  ];

  return (
    <section className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.h2 variants={fadeUpVariant} className="text-3xl font-heading mb-12 text-center">
          Standard Audit Workflow
        </motion.h2>

        <div className="relative">
          <div className="hidden md:block absolute top-8 left-0 w-full h-0.5 bg-border z-0" />

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 relative z-10">
            {steps.map((step) => (
              <motion.div key={step.num} variants={fadeUpVariant}>
                <Card size="sm" className="items-center text-center py-5 h-full">
                  <CardContent className="flex flex-col items-center gap-3 px-(--card-spacing)">
                    <div className="w-12 h-12 rounded-base bg-main text-black border-2 border-border flex items-center justify-center font-mono text-lg font-heading shadow-shadow">
                      {step.num}
                    </div>
                    <div>
                      <h4 className="font-heading text-foreground text-sm mb-1">{step.title}</h4>
                      <p className="text-xs font-mono text-muted-foreground">{step.desc}</p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
};
