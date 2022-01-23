// Simcenter STAR-CCM+ macro: automation_macro.java
// Written by Simcenter STAR-CCM+ 15.04.008
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.base.report.*;
import star.flow.*;
import star.vis.*;
import java.io.*;

// This likely only works for a case where:
// One vent, one inlet
// Inlet doesn't move

// Things to check:
// Seems you cannot open or close simulations using macro
// Test with GUI using shell
// Set new vent/port regions to not have any physics continua
// Fix the appearance of ports and flow scene with updated regions

public class automation_macro extends StarMacro {

  public void execute() {
    execute0();
    // D:/Ahmeds Files/PhD/Simulations/Optimisation/1-Optimisation.sim
    //execute1(); // May not be needed
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    Solution solution_0 = 
      simulation_0.getSolution();

    solution_0.clearSolution();

    ExpressionReport expressionReport_ventx1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location X1"));

    expressionReport_ventx1.setDefinition("-0.006");

    ExpressionReport expressionReport_venty1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location Y1"));

    expressionReport_venty1.setDefinition("-0.003");

    ExpressionReport expressionReport_ventx2 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location X2"));

    expressionReport_ventx2.setDefinition("-0.027"); 

    ExpressionReport expressionReport_venty2 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location Y2"));

    expressionReport_venty2.setDefinition("0.036"); 

    ExpressionReport expressionReport_injectionx1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Injection Location X"));

    expressionReport_injectionx1.setDefinition("-0.0065");

    ExpressionReport expressionReport_injectiony1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Injection Location Y"));

    expressionReport_injectiony1.setDefinition("0.01");

    MeshManager meshManager_0 = 
      simulation_0.getMeshManager();

    UserFieldFunction userFieldFunction_1 = 
      ((UserFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Injection Port Location"));

    UserFieldFunction userFieldFunction_2 = 
      ((UserFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Vent Port Location"));

    Region region_0 = 
      simulation_0.getRegionManager().getRegion("Region 1");
    
    Region region_1 = 
      simulation_0.getRegionManager().getRegion("Discontinous Region 1");

    Region region_2 = 
      simulation_0.getRegionManager().getRegion("Vent Port");

    Region region_3 = 
      simulation_0.getRegionManager().getRegion("Injection Port");

    Region region_4 = 
      simulation_0.getRegionManager().getRegion("Invalids of Region 1");


    ////////// RECOMBINING ALL HOLES //////////
    // Combine VENT and Domain, then look to resplit
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_0, region_2}), true, true, 0.02, true);


    // Combine PORT and Domain, then look to resplit
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_0, region_3}), true, true, 0.02, true);


    // Before resplitting, we look to return all cells to their original place
    // Split combined region by porosity fct (to prevent assimilation of non-domain cells)
    // We will use an if function here to make it run smoothly
    // NOT DONE YET



    ////////// CREATING THE VENT HOLES //////////
    // Split all regions to reobtain new VENT positons
    meshManager_0.splitRegionsByFunction(userFieldFunction_2, new NeoObjectVector(new Object[] {region_0, region_1, region_4}));

    // We must consider if we get more than one region when we have more than one VENT
    Region region_new_vent_0 = simulation_0.getRegionManager().getRegion("Region 1 2");
    
    // If we get the other regions within the vent zone, we combine them
    if (simulation_0.getRegionManager().has("Discontinous Region 1 2")){
    Region region_new_vent_1 = simulation_0.getRegionManager().getRegion("Discontinous Region 1 2");
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_new_vent_0, region_new_vent_1}), true, true, 0.02, true);
    }

    if (simulation_0.getRegionManager().has("Invalids of Region 1 2")){
    Region region_new_vent_2 = simulation_0.getRegionManager().getRegion("Invalids of Region 1 2");
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_new_vent_0, region_new_vent_2}), true, true, 0.02, true);
    }
    
    region_new_vent_0.setPresentationName("Vent Port");


    ////////// REAPPLYING ALL VALUES FOR VENT //////////
    Boundary boundary_newventboundary = 
      region_0.getBoundaryManager().getBoundary("internal-1");

    boundary_newventboundary.setPresentationName("Vent Boundary"); // Rename to Vent Boundary
    
    PressureBoundary pressureBoundary_0 = 
      ((PressureBoundary) simulation_0.get(ConditionTypeManager.class).get(PressureBoundary.class));
    
    boundary_newventboundary.setBoundaryType(pressureBoundary_0);

    BackflowSpecification backflowSpecification_0 = 
      boundary_newventboundary.getConditions().get(BackflowSpecification.class);
  
    backflowSpecification_0.getReversedFlowPressureOption().setSelected(ReversedFlowPressureOption.Type.STATIC);
  
    backflowSpecification_0.getReversedFlowScalarOption().setSelected(ReversedFlowScalarOption.Type.EXTRAPOLATED);
  
    VolumeFractionProfile volumeFractionProfile_0 = 
      boundary_newventboundary.getValues().get(VolumeFractionProfile.class);
  
    volumeFractionProfile_0.getMethod(ConstantArrayProfileMethod.class).getQuantity().setArray(new DoubleVector(new double[] {1.0, 0.0}));
  
    StaticPressureProfile staticPressureProfile_0 = 
      boundary_newventboundary.getValues().get(StaticPressureProfile.class);
  
    staticPressureProfile_0.getMethod(ConstantScalarProfileMethod.class).getQuantity().setValue(0.0);
  
    Units units_0 = 
      ((Units) simulation_0.getUnitsManager().getObject("Pa"));
  
    staticPressureProfile_0.getMethod(ConstantScalarProfileMethod.class).getQuantity().setUnits(units_0);
    ////////// END OF REAPPLYING VENT VALUES //////////
    

    ////////// CREATING THE PORT HOLES //////////
    // Split all regions to reobtain new PORT positons
    meshManager_0.splitRegionsByFunction(userFieldFunction_1, new NeoObjectVector(new Object[] {region_0, region_1, region_4}));

    // We must consider if we get more than one region when we have more than one VENT
    Region region_new_port_0 = simulation_0.getRegionManager().getRegion("Region 1 2");
    

    // If we get the other regions within the vent zone, we combine them
    if (simulation_0.getRegionManager().has("Discontinous Region 1 2")){
    Region region_new_port_1 = simulation_0.getRegionManager().getRegion("Discontinous Region 1 2");
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_new_port_0, region_new_port_1}), true, true, 0.02, true);
    }

    if (simulation_0.getRegionManager().has("Invalids of Region 1 2")){
    Region region_new_port_2 = simulation_0.getRegionManager().getRegion("Invalids of Region 1 2");
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_new_port_0, region_new_port_2}), true, true, 0.02, true);
    }
    
    region_new_port_0.setPresentationName("Injection Port");


    ////////// REAPPLYING ALL VALUES FOR PORT //////////
    Boundary boundary_newportboundary = 
      region_0.getBoundaryManager().getBoundary("internal-1");

    boundary_newportboundary.setPresentationName("Injection Boundary");
    
    PressureBoundary pressureBoundary_1 = 
      ((PressureBoundary) simulation_0.get(ConditionTypeManager.class).get(PressureBoundary.class));
    
    boundary_newportboundary.setBoundaryType(pressureBoundary_1);

    BackflowSpecification backflowSpecification_1 = 
      boundary_newportboundary.getConditions().get(BackflowSpecification.class);
  
    backflowSpecification_1.getReversedFlowPressureOption().setSelected(ReversedFlowPressureOption.Type.STATIC);
  
    backflowSpecification_1.getReversedFlowScalarOption().setSelected(ReversedFlowScalarOption.Type.EXTRAPOLATED);
  
    VolumeFractionProfile volumeFractionProfile_1 = 
      boundary_newportboundary.getValues().get(VolumeFractionProfile.class);
  
    volumeFractionProfile_1.getMethod(ConstantArrayProfileMethod.class).getQuantity().setArray(new DoubleVector(new double[] {0.0, 1.0}));
  
    StaticPressureProfile staticPressureProfile_1 = 
      boundary_newportboundary.getValues().get(StaticPressureProfile.class);
  
    staticPressureProfile_1.setMethod(RadialEquilibriumProfile.class);

    staticPressureProfile_1.getMethod(RadialEquilibriumProfile.class).getHubPressure().setDefinition("${Injection Port Pressure}");
    ////////// END OF REAPPLYING PORT VALUES //////////


    ////////// SETTING CORRECT PHYS CONTINUA FOR REGIONS //////////
    PhysicsContinuum physicsContinuum_0 = 
      ((PhysicsContinuum) simulation_0.getContinuumManager().getContinuum("Physics 1"));

    physicsContinuum_0.erase(region_new_vent_0); // Removes continua for the ports and vents

    physicsContinuum_0.erase(region_new_port_0);


    ////////// RE-ADJUSTING SCENE //////////
    Scene scene_0 = 
      simulation_0.getSceneManager().getScene("Ports and Flow");

    // Flow displayer
    ScalarDisplayer scalarDisplayer_3 = 
      ((ScalarDisplayer) scene_0.getDisplayerManager().getDisplayer("Flow"));

    Boundary boundary_mainregion0 = 
      region_0.getBoundaryManager().getBoundary("Default");

    Boundary boundary_mainregion1 = 
      region_0.getBoundaryManager().getBoundary("Injection Boundary");

    Boundary boundary_mainregion2 = 
      region_0.getBoundaryManager().getBoundary("Vent Boundary");
    
    scalarDisplayer_3.getInputParts().setQuery(null); // Clear all inputs
    
    scalarDisplayer_3.getInputParts().setObjects(region_0, boundary_mainregion0, boundary_mainregion1, boundary_mainregion2);

    // Injection displayer
    ScalarDisplayer scalarDisplayer_5 = 
      ((ScalarDisplayer) scene_0.getDisplayerManager().getDisplayer("Injection"));

    scalarDisplayer_5.getInputParts().setQuery(null);
    scalarDisplayer_5.getInputParts().setObjects(region_new_port_0);
    
    // Vent displayer
    ScalarDisplayer scalarDisplayer_4 = 
      ((ScalarDisplayer) scene_0.getDisplayerManager().getDisplayer("Venting"));

    scalarDisplayer_4.getInputParts().setQuery(null);
    scalarDisplayer_4.getInputParts().setObjects(region_new_vent_0);
    ////////// END OF SCENE RE-ADJUSTMENT //////////
    

    // Starting solution
    solution_0.initializeSolution();

    //ResidualPlot residualPlot_0 = 
    //  ((ResidualPlot) simulation_0.getPlotManager().getPlot("Residuals"));

    // residualPlot_0.open();

    simulation_0.getSimulationIterator().step(10);


    ////////// SAVING SCENE IMAGE //////////
    CurrentView currentView_0 = 
      scene_0.getCurrentView();

    currentView_0.setInput(new DoubleVector(new double[] {8.785244226997861E-4, -0.0011749124535490665, -8.637662010675118E-4}), new DoubleVector(new double[] {8.785244226997861E-4, -0.0011749124535490665, 0.20513410377306918}), new DoubleVector(new double[] {-1.0, 0.0, 0.0}), 0.8660254037844386, 0, 30.0);

    scene_0.printAndWait(resolvePath("D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Images/Optimisation_Flow_1.png"), 1, 1200, 800, true, true);

    
    ////////// SAVING FILL EFFICIENCY DATA //////////
    MonitorPlot monitorPlot_0 = 
    ((MonitorPlot) simulation_0.getPlotManager().getPlot("Fill Efficiency Monitor Plot"));

    //monitorPlot_0.open(); // May not be needed...

    MonitorDataSet monitorDataSet_0 = 
      ((MonitorDataSet) monitorPlot_0.getDataSetManager().getDataSet("Fill Efficiency Monitor"));

    // Last string arg below indicates field delimiter (separator)
    monitorPlot_0.getDataSetManager().writeCSVDataSet(monitorDataSet_0, resolvePath("D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Data/Fill_eff_dataset_1.csv"), ",");
    

    ////////// SAVING FILE //////////
    simulation_0.saveState("D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/SaveFiles/1-Optimisation_auto.sim");
  }

  //private void execute1() {
  //} // May not be needed...
}
