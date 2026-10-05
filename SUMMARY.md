# Table of contents

* [Fomoxa for Unity](README.md)

## Getting started

* [Introduction](getting-started/introduction.md)
* [Installation](getting-started/installation.md)
* [Your first project](getting-started/first-project.md)
* [Your first server](getting-started/first-server.md)
* [Your first client](getting-started/first-client.md)
* [Troubleshooting](getting-started/troubleshooting.md)

## Concepts

* [Architecture](concepts/architecture.md)
* [Networking model](concepts/networking-model.md)
* [Ticks and timing](concepts/tick.md)
* [Authority](concepts/authority.md)
* [Replication](concepts/replication.md)
* [Prediction](concepts/prediction.md)
* [Deterministic simulation](concepts/deterministic-simulation.md)
* [Lifecycle](concepts/lifecycle.md)

## Core

* [NetworkManager](core/network-manager.md)
* [Server](core/server.md)
* [Client](core/client.md)
* [Host mode](core/host-mode.md)
* [NetworkObject](core/network-object.md)
* [NetworkBehaviour](core/network-behaviour.md)
* [Spawning](core/spawning.md)
* [Ownership](core/ownership.md)
* [Observers](core/observers.md)
* [Network scenes](core/scenes.md)

## Messaging

* [Models and codecs](messaging/models.md)
* [RPCs](messaging/rpc.md)
* [Channels and reliability](messaging/channels.md)
* [Raw messages](messaging/messages.md)

## Synchronization

* [State](synchronization/state.md)
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

## Transports

* [Overview](transports/overview.md)
* [UDP](transports/udp.md)
* [TCP](transports/tcp.md)
* [WebSocket](transports/websocket.md)
* [Multiple transports](transports/multi-transport.md)
* [Loopback](transports/loopback.md)
* [Custom transport](transports/custom-transport.md)

## Server

* [Dedicated server](server/dedicated-server.md)
* [Deployment](server/deployment.md)
* [Server console](server/server-console.md)

## Unity

* [Editor integration](unity/editor-integration.md)
* [WebGL](unity/webgl.md)

## Advanced

* [Custom codecs and Unity types](advanced/custom-codecs.md)
* [Performance](advanced/performance.md)
* [Debugging](advanced/debugging.md)

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
