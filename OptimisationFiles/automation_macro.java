// Simcenter STAR-CCM+ macro: automation_macro.java
// Written by Simcenter STAR-CCM+ 15.04.008
package macro;

import java.util.*;
import java.util.Collection;
import java.io.*;

import star.common.*;
import star.base.neo.*;
import star.base.report.*;
import star.flow.*;
import star.vis.*;

// This likely only works for a case where:
// One vent, one inlet
// Inlet doesn't move

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

    expressionReport_ventx1.setDefinition("-0.030600000000000002");

    ExpressionReport expressionReport_venty1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location Y1"));

    expressionReport_venty1.setDefinition("0.0396");

    ExpressionReport expressionReport_ventx2 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location X2"));

    expressionReport_ventx2.setDefinition("1.0064");

    ExpressionReport expressionReport_venty2 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Vent Location Y2"));

    expressionReport_venty2.setDefinition("1.0066");

    ExpressionReport expressionReport_injectionx1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Injection Location X"));

    expressionReport_injectionx1.setDefinition("0.0231");

    ExpressionReport expressionReport_injectiony1 = 
      ((ExpressionReport) simulation_0.getReportManager().getReport("Injection Location Y"));

    expressionReport_injectiony1.setDefinition("-0.014099999999999999");

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


    ////////// RECOMBINING WALL BOUNDARIES (PRIMARY) //////////
    // Combining all boundaries in vent holes into 'Default'
    Boundary vent_wall = region_2.getBoundaryManager().getBoundary("internal-0");

    Collection<Boundary> allVentBoundaries = region_2.getBoundaryManager().getBoundaries();
    for (Boundary vent_bound : allVentBoundaries) {
      if (! vent_bound.getPresentationName().contains("internal-0") ){
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {vent_wall, vent_bound}));
      }
    }

    // Combining all boundaries in port holes into 'Default'
    Boundary port_wall = region_3.getBoundaryManager().getBoundary("internal-0");

    Collection<Boundary> allPortBoundaries = region_3.getBoundaryManager().getBoundaries();
    for (Boundary port_bound : allPortBoundaries) {
      if (! port_bound.getPresentationName().contains("internal-0") ){ // If NOT default
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {port_wall, port_bound}));
      }
    }

    // Combining all boundaries in invalid region into 'Default'
    Boundary invalids_wall = region_4.getBoundaryManager().getBoundary("Default");

    Collection<Boundary> allInvalidsBoundaries = region_4.getBoundaryManager().getBoundaries();
    for (Boundary invalids_bounds: allInvalidsBoundaries) {
      if (! invalids_bounds.getPresentationName().contains("Default") ){
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {invalids_wall, invalids_bounds}));
      }
    }


    // Combining all boundaries in disconnected region into 'Default'
    Boundary disconn_wall = region_1.getBoundaryManager().getBoundary("Default");

    Collection<Boundary> allDisconnBoundaries = region_1.getBoundaryManager().getBoundaries();
    for (Boundary disconn_bounds: allDisconnBoundaries) {
      if (! disconn_bounds.getPresentationName().contains("Default") ){
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {disconn_wall, disconn_bounds}));
      }
    }

    // Combining all boundaries in primary domain region into 'Default' first time (redundant)
    Boundary domain_wall = region_0.getBoundaryManager().getBoundary("Default");

    Collection<Boundary> allDomainBoundaries = region_0.getBoundaryManager().getBoundaries();
    for (Boundary domain_bounds: allDomainBoundaries) {
      if (! domain_bounds.getPresentationName().contains("Default") ){
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {domain_wall, domain_bounds}));
      }
    }
    ////////// END OF RECOMBINING WALL BOUNDARIES //////////


    ////////// RECOMBINING ALL HOLES //////////
    // Combine VENT and Domain, then look to resplit
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_0, region_2}), true, true, 0.02, true);


    // Combine PORT and Domain, then look to resplit
    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_0, region_3}), true, true, 0.02, true);


    ////////// RETURNING CELLS TO ORIGINAL FORM //////////
    UserFieldFunction userFieldFunction_0 = 
      ((UserFieldFunction) simulation_0.getFieldFunctionManager().getFunction("Porosity"));

    // First Attempt removes cells outside of domain (<min porosity)
    meshManager_0.removeInvalidCells(userFieldFunction_0, new NeoObjectVector(new Object[] {region_0}), NeoProperty.fromString("{\'minimumContiguousFaceArea\': 0.0, \'minimumCellVolumeEnabled\': false, \'minimumVolumeChangeEnabled\': false, \'functionOperator\': 0, \'minimumContiguousFaceAreaEnabled\': false, \'minimumFaceValidityEnabled\': false, \'functionValue\': 0.08, \'functionEnabled\': true, \'function\': \'Porosity\', \'minimumVolumeChange\': 0.5, \'minimumCellVolume\': 0.0, \'minimumCellQualityEnabled\': false, \'minimumCellQuality\': 1.0E-8, \'minimumDiscontiguousCells\': 100, \'minimumDiscontiguousCellsEnabled\': true, \'minimumFaceValidity\': 0.51}"));
    
    // We recombine the non-domain cells into one region (if there is any) first.
    // This is because there is can't be disconnected cells in hole if no non-domain cells
    if (simulation_0.getRegionManager().has("Cells deleted from Region 1")){
    Region region_extracted_invalid = 
      simulation_0.getRegionManager().getRegion("Cells deleted from Region 1");

    meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_4, region_extracted_invalid}), true, true, 0.02, true);

    // Second Attempt removes cells now disconnected from main domain
    meshManager_0.removeInvalidCells(userFieldFunction_0, new NeoObjectVector(new Object[] {region_0}), NeoProperty.fromString("{\'minimumContiguousFaceArea\': 0.0, \'minimumCellVolumeEnabled\': false, \'minimumVolumeChangeEnabled\': false, \'functionOperator\': 0, \'minimumContiguousFaceAreaEnabled\': false, \'minimumFaceValidityEnabled\': false, \'functionValue\': 0.08, \'functionEnabled\': true, \'function\': \'Porosity\', \'minimumVolumeChange\': 0.5, \'minimumCellVolume\': 0.0, \'minimumCellQualityEnabled\': false, \'minimumCellQuality\': 1.0E-8, \'minimumDiscontiguousCells\': 100, \'minimumDiscontiguousCellsEnabled\': true, \'minimumFaceValidity\': 0.51}"));

      if (simulation_0.getRegionManager().has("Cells deleted from Region 1")){
        // Recombining disconnected cells into one region
        Region region_extracted_disconn = 
          simulation_0.getRegionManager().getRegion("Cells deleted from Region 1");

        meshManager_0.combineRegions(new NeoObjectVector(new Object[] {region_1, region_extracted_disconn}), true, true, 0.02, true);
      }
    }

    // Combining all boundaries in primary domain region into 'Default' second time (to remove odd BCs)
    Boundary domain_wall2 = region_0.getBoundaryManager().getBoundary("Default");

    Collection<Boundary> allDomainBoundaries2 = region_0.getBoundaryManager().getBoundaries();
    for (Boundary domain_bounds2: allDomainBoundaries2) {
      if (! domain_bounds2.getPresentationName().contains("Default") ){
        meshManager_0.combineBoundaries(new NeoObjectVector(new Object[] {domain_wall2, domain_bounds2}));
      }
    }

    
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

    simulation_0.getSimulationIterator().run();


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
    simulation_0.saveState("D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/SaveFiles/1-Optimisation_auto_1.sim");
  
    //CLOSING SIMULATION
    simulation_0.close(ServerConnection.CloseOption.ForceClose);
    System.exit(0);
  }

  //private void execute1() {
  //} // May not be needed...
}
