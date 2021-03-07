FOREST_SEED = "-5603130799377933031"
DESERT_SEED = "400009"


class MissionData:

    def __init__(self):
        self.start_time = 6000
        self.allow_passage_of_time = False
        self.seed = DESERT_SEED
        self.entity_ranges = (8, 2, 6)
        self.name = "SteveBot"

        self.night_vision = True

        grid_obs_range_x = (-30, 30)
        grid_obs_range_y = (-10, 10)
        grid_obs_range_z = (-35, 35)
        self.grid_obs_range = [grid_obs_range_x, grid_obs_range_y, grid_obs_range_z]

    def get_xml(self):
        passage_of_time = "true" if self.allow_passage_of_time else "false"
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
            <About>
                <Summary>Behaviour Tree Malmo</Summary>
            </About>

            <ServerSection>
                <ServerInitialConditions>
                    <Time>
                        <StartTime>{self.start_time}</StartTime>
                        <AllowPassageOfTime>{passage_of_time}</AllowPassageOfTime>
                    </Time>
                </ServerInitialConditions>
                <ServerHandlers>
                    <DefaultWorldGenerator seed="{self.seed}" />
                </ServerHandlers>
            </ServerSection>

            <AgentSection mode="Survival">
                <Name>{self.name}</Name>
                <AgentStart>
                    <Placement x="247" y="68.0" z="232" pitch="18"/>
                </AgentStart>
                <AgentHandlers>
                    <ContinuousMovementCommands/>
                    <InventoryCommands />
                    <SimpleCraftCommands/>
                    <MissionQuitCommands/>
                    <ChatCommands />                    
                    <ObservationFromRay/>
                    <ObservationFromFullStats/>
                    <ObservationFromFullInventory/>
                    <ObservationFromNearbyEntities>
                        <Range name="entities" xrange="{self.entity_ranges[0]}" yrange="{self.entity_ranges[1]}" zrange="{self.entity_ranges[2]}"/>
                    </ObservationFromNearbyEntities>
                    <ObservationFromGrid>				
                        <Grid absoluteCoords="false" name="me">				
                            <min x="{self.grid_obs_range[0][0]}" y="{self.grid_obs_range[1][0]}" z="{self.grid_obs_range[2][0]}"/>                    
                            <max x="{self.grid_obs_range[0][1]}" y="{self.grid_obs_range[1][1]}" z="{self.grid_obs_range[2][1]}"/>				
                        </Grid>			
                    </ObservationFromGrid>
                </AgentHandlers>
            </AgentSection>
            </Mission>'''

    def get_grid_size(self):
        return [axis[1] - axis[0] + 1 for axis in self.grid_obs_range]
