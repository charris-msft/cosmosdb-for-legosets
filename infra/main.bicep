targetScope = 'subscription'

@minLength(1)
@maxLength(64)
param environmentName string

@minLength(1)
param location string

@description('Principal ID of the user running the deployment')
param principalId string

var resourceSuffix = take(uniqueString(subscription().id, environmentName, location), 6)
var tags = { 'azd-env-name': environmentName }

resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module cosmos './modules/cosmos.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    location: location
    tags: tags
    environmentName: environmentName
    resourceSuffix: resourceSuffix
    principalId: principalId
  }
}

output AZURE_RESOURCE_GROUP string = rg.name
output COSMOS_ENDPOINT string = cosmos.outputs.cosmosEndpoint
output COSMOS_DATABASE string = cosmos.outputs.cosmosDatabaseName
output COSMOS_CONTAINER string = cosmos.outputs.cosmosContainerName
