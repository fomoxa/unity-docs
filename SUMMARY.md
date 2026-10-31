# Table of contents

* [Fomoxa for Unity](README.md)

## Get started

* [Introduction](getting-started/introduction.md)
* [Installation](getting-started/installation.md)
* [Tutorial: your first multiplayer game](getting-started/tutorial/README.md)
  * [1. Set up the project](getting-started/tutorial/project-setup.md)
  * [2. Start a server](getting-started/tutorial/server.md)
  * [3. Connect clients](getting-started/tutorial/clients.md)
* [Troubleshooting](getting-started/troubleshooting.md)
* [Release notes](release-notes.md)

## Learn the basics

* [How the package is built](concepts/architecture.md)
* [Server, clients and messages](concepts/networking-model.md)
* [Ticks and timing](concepts/tick.md)
* [Authority](concepts/authority.md)
* [Replication](concepts/replication.md)
* [Prediction](concepts/prediction.md)
* [Deterministic simulation](concepts/deterministic-simulation.md)
* [Lifecycle](concepts/lifecycle.md)

## Connections

* [NetworkManager](connections/network-manager.md)
* [Server](connections/server.md)
* [Client](connections/client.md)
* [Authentication](connections/authentication.md)
* [Host mode](connections/host-mode.md)
* [Server transfer](connections/transfer.md)
* [Transports](connections/transports/README.md)
  * [UDP](connections/transports/udp.md)
  * [Encrypted UDP](connections/transports/encrypted-udp.md)
  * [Encrypted WebSocket](connections/transports/encrypted-websocket.md)
  * [TCP](connections/transports/tcp.md)
  * [WebSocket](connections/transports/websocket.md)
  * [Client TLS](connections/transports/tls.md)
  * [Multiple transports](connections/transports/multi-transport.md)
  * [Loopback](connections/transports/loopback.md)
  * [Custom transport](connections/transports/custom-transport.md)

## Network objects

* [NetworkObject](objects/network-object.md)
* [NetworkBehaviour](objects/network-behaviour.md)
* [Spawning](objects/spawning.md)
* [Ownership](objects/ownership.md)
* [Observers](objects/observers.md)
* [Network scenes](objects/scenes.md)

## Messaging

* [Models and codecs](messaging/models.md)
* [RPCs](messaging/rpc.md)
* [Channels and reliability](messaging/channels.md)
* [Raw messages](messaging/messages.md)

## Synchronization

* [State](synchronization/state.md)
* [Collections](synchronization/collections.md)
* [NetworkTransform](synchronization/transform.md)
* [NetworkAnimator](synchronization/animator.md)

## Prediction

* [Overview](prediction/overview.md)
* [Input](prediction/input.md)
* [Reconciliation](prediction/reconciliation.md)
* [Rollback with physics](prediction/rollback.md)

## Physics

* [Overview](physics/overview.md)
* [PhysicsBody](physics/physics-body.md)
* [Contact events](physics/contacts.md)
* [Physics architecture](physics/architecture.md)

## Deploy

* [Dedicated server](deploy/dedicated-server.md)
* [Deployment](deploy/deployment.md)
* [Game backend](deploy/backend.md)
* [Cluster](deploy/cluster.md)
* [Agones](deploy/agones.md)
* [WebGL](deploy/webgl.md)

## Advanced

* [Editor integration](advanced/editor-integration.md)
* [Custom codecs and Unity types](advanced/custom-codecs.md)
* [Performance](advanced/performance.md)
* [Debugging](advanced/debugging.md)

## Rapier physics

* [Overview](rapier/overview.md)
* [Setup](rapier/setup.md)
* [Bodies and colliders](rapier/bodies.md)
* [Contact events](rapier/contacts.md)
* [Determinism](rapier/determinism.md)

## Console server

* [Overview](console-server/overview.md)
* [The project](console-server/project.md)
* [The runtime](console-server/runtime.md)
* [Physics](console-server/physics.md)
* [Reference](console-server/reference.md)

## Examples

* [Red Runner](examples/redrunner/README.md)
  * [Offline baseline](examples/redrunner/offline-baseline.md)
  * [Offline to online](examples/redrunner/offline-to-online/README.md)
    * [Step 01: Network foundation](examples/redrunner/offline-to-online/step-01-network-foundation.md)
    * [Step 02: Shared level](examples/redrunner/offline-to-online/step-02-shared-level.md)
    * [Step 03: Player spawning](examples/redrunner/offline-to-online/step-03-player-spawning.md)
    * [Step 04: Player input](examples/redrunner/offline-to-online/step-04-player-input.md)
    * [Step 05: Prediction and reconciliation](examples/redrunner/offline-to-online/step-05-prediction-and-reconciliation.md)
    * [Step 06: Death and respawn](examples/redrunner/offline-to-online/step-06-death-and-respawn.md)
    * [Step 07: Moving hazards](examples/redrunner/offline-to-online/step-07-moving-hazards.md)
    * [Step 08: Two clients](examples/redrunner/offline-to-online/step-08-two-clients.md)
    * [Step 09: Final online game](examples/redrunner/offline-to-online/step-09-final-online-game.md)
  * [Online architecture](examples/redrunner/architecture.md)
  * [Troubleshooting](examples/redrunner/troubleshooting.md)
  * [Rapier and a console server](examples/redrunner/rapier-and-console/README.md)
    * [Step 10: Rapier backend](examples/redrunner/rapier-and-console/step-10-rapier-backend.md)
    * [Step 11: Simulation library](examples/redrunner/rapier-and-console/step-11-simulation-library.md)
    * [Step 12: Level catalogue](examples/redrunner/rapier-and-console/step-12-level-catalogue.md)
    * [Step 13: Console server](examples/redrunner/rapier-and-console/step-13-console-server.md)

## Reference

* [API index](reference/api.md)
* [NetworkManager](reference/network-manager.md)
* [ServerManager](reference/server-manager.md)
* [ClientManager](reference/client-manager.md)
* [TimeManager](reference/time-manager.md)
* [NetworkObject and NetworkBehaviour](reference/network-object.md)
* [Components](reference/components.md)
* [Physics API](reference/physics.md)
* [Messaging API](reference/messaging.md)
* [Configuration](reference/configuration.md)
* [Attributes](reference/attributes.md)
* [Events and callbacks](reference/callbacks.md)
* [Errors and stop reasons](reference/errors.md)
* [Glossary](reference/glossary.md)

## Contributing

* [Development](contributing/development.md)
* [Documentation](contributing/documentation.md)
