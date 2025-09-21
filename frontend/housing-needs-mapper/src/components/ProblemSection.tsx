import { Home } from "lucide-react";

const ProblemSection = () => {
  return (
    <section className="py-section bg-surface">
      <div className="container mx-auto px-container">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-light rounded-full mb-8">
            <Home className="w-10 h-10 text-primary" />
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold font-heading text-foreground mb-8">
            The Problem
          </h2>
          
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-3xl mx-auto">
            Rising housing costs are pushing low-income families into poor living conditions. 
            Without reliable data, it's hard to know where affordable housing is needed the most. 
            Communities struggle to make informed decisions about where to invest resources 
            and how to best serve families in need.
          </p>
        </div>
      </div>
    </section>
  );
};

export default ProblemSection;