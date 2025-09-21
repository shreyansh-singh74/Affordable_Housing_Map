import { TrendingUp, Users, MapPin } from "lucide-react";

const ImpactSection = () => {
  const stats = [
    {
      icon: <Users className="w-8 h-8 text-primary" />,
      number: "10,000+",
      label: "Families Identified in Need",
    },
    {
      icon: <MapPin className="w-8 h-8 text-secondary" />,
      number: "25+",
      label: "Communities Analyzed",
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-accent" />,
      number: "85%",
      label: "Accuracy in Need Prediction",
    },
  ];

  return (
    <section className="py-section bg-gradient-hero">
      <div className="container mx-auto px-container">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold font-heading text-foreground mb-8">
            Why It Matters
          </h2>
          
          <div className="max-w-4xl mx-auto">
            <p className="text-lg md:text-xl text-muted-foreground leading-relaxed mb-12">
              Affordable Housing Needs Mapper empowers policymakers, NGOs, and communities 
              with the insights they need to plan smarter housing projects. By using data-driven 
              approaches, we help ensure resources are allocated where they'll have the greatest impact.
            </p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {stats.map((stat, index) => (
            <div 
              key={index}
              className="text-center bg-card/80 backdrop-blur-sm rounded-lg p-8 shadow-md border border-border"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-surface rounded-full mb-4">
                {stat.icon}
              </div>
              <div className="text-3xl font-bold font-heading text-foreground mb-2">
                {stat.number}
              </div>
              <div className="text-muted-foreground font-medium">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ImpactSection;