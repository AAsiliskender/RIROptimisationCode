// Simcenter STAR-CCM+ macro: automation_macro.java
// Written by Simcenter STAR-CCM+ 15.04.008
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.base.report.*;

public class automation_macro extends StarMacro {

  public void execute() {
    execute0();
    // D:/Ahmeds Files/PhD/Simulations/Optimisation/1-Optimisation.sim
    execute1();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    Solution solution_0 = 
      simulation_0.getSolution();

    solution_0.clearSolution();

    ExpressionReport expressionReport_1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location X1"));

    expressionReport_1.setDefinition("-0.006");

    ExpressionReport expressionReport_2 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location Y1"));

    expressionReport_2.setDefinition("-0.003");

    MeshManager meshManager_0 = 
      simulation_0.getMeshManager();

    UserFieldFunction userFieldFunction_1 = 
      ((UserFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Injection Port Location"));

    Region region_0 = 
      simulation_0.getRegionManager().getRegion("Region 1");

    meshManager_0.splitRegionsByFunction(userFieldFunction_1, new NeoObjectVector(new Object[] {region_0}));


    UserFieldFunction userFieldFunction_2 = 
      ((UserFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Vent Port Location"));

    meshManager_0.splitRegionsByFunction(userFieldFunction_2, new NeoObjectVector(new Object[] {region_0}));

    Boundary boundary_0 = 
      region_0.getBoundaryManager().getBoundary("internal-1");

    Boundary boundary_1 = 
      region_0.getBoundaryManager().getBoundary("Vent Boundary");

    boundary_0.copyProperties(boundary_1);

    Region region_1 = 
      simulation_0.getRegionManager().getRegion("Region 1 2");

    Region region_2 = 
      simulation_0.getRegionManager().getRegion("Vent Port");

    region_1.copyProperties(region_2);

    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_0, region_2}), true, true, 0.02, true);

    boundary_0.setPresentationName("Vent Boundary");

    region_1.setPresentationName("Vent Port");

    solution_0.initializeSolution();

    ResidualPlot residualPlot_0 = 
      ((ResidualPlot) simulation_0.getPlotManager().getPlot("Residuals"));

    // residualPlot_0.open();

    simulation_0.getSimulationIterator().step(1);

    simulation_0.saveState("D:\\Ahmeds Files\\PhD\\Simulations\\Optimisation\\1-Optimisation.sim");
  }

  private void execute1() {
  }
}
