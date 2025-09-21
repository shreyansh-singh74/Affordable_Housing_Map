import dataIcon from "@/assets/data-icon.jpg";
import communityIcon from "@/assets/community-icon.jpg";
import actionIcon from "@/assets/action-icon.jpg";

const SolutionSection = () => {
  const solutions = [
    {
      icon: dataIcon,
      title: "Data Driven Insights",
      description: "We combine census data with real estate trends to create comprehensive housing need assessments.",
    },
    {
      icon: communityIcon,
      title: "Community Focused",
      description: "We identify where families are struggling the most, prioritizing vulnerable populations and underserved areas.",
    },
    {
      icon: actionIcon,
      title: "Actionable Recommendations",
      description: "We suggest optimal locations for housing projects near jobs, schools, and transportation networks.",
    },
  ];

  return (
    <section className="py-section bg-background">
      <div className="container mx-auto px-container">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold font-heading text-foreground mb-6">
            Our Approach
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A comprehensive solution that combines data science with community insights
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {solutions.map((solution, index) => (
            <div 
              key={index}
              className="group bg-card rounded-lg p-8 shadow-md hover:shadow-lg transition-all duration-300 hover:-translate-y-2 border border-border"
            >
              <div className="flex items-center justify-center w-20 h-20 rounded-lg mb-6 mx-auto overflow-hidden bg-gradient-card">
                <img 
                  src={solution.icon} 
                  alt={solution.title}
                  className="w-12 h-12 object-cover rounded"
                />
              </div>
              
              <h3 className="text-xl font-semibold font-heading text-foreground mb-4 text-center">
                {solution.title}
              </h3>
              
              <p className="text-muted-foreground leading-relaxed text-center">
                {solution.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SolutionSection;