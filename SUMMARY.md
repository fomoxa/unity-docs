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
  * [Steam](connections/transports/steam.md)
  * [Client TLS](connections/transports/tls.md)
  * [Multiple transports](connections/transports/multi-transport.md)
  * [Loopback](connections/transports/loopback.md)
  * [Network simulation](connections/transports/simulated.md)
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
* [Physics queries](physics/queries.md)
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
* [Joints](rapier/joints.md)
* [Character controller](rapier/character-controller.md)
* [Effectors](rapier/effectors.md)
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
* [Infra demo](examples/infra-demo/README.md)
  * [Prepare the environment (Ubuntu or WSL2)](examples/infra-demo/getting-started/prepare-environment.md)
  * [Quick start with the mock cluster (no Kubernetes)](examples/infra-demo/getting-started/quickstart-mock-cluster.md)
  * [Deploy to Kubernetes (k3d + Agones), step by step](examples/infra-demo/deploy/README.md)
    * [Kubernetes concepts used in this demo](examples/infra-demo/deploy/concepts.md)
    * [Prepare, free ports, keys and certificate](examples/infra-demo/deploy/01-prepare-and-keys.md)
    * [Get the gateway source and build the Docker images](examples/infra-demo/deploy/02-build-images.md)
    * [Create the k3d cluster, install Agones, import images](examples/infra-demo/deploy/03-cluster-and-agones.md)
    * [Namespace and secrets](examples/infra-demo/deploy/04-secrets.md)
    * [Apply the manifests in order](examples/infra-demo/deploy/05-apply-manifests.md)
    * [Check the whole cluster and check from the client side](examples/infra-demo/deploy/06-verify-cluster.md)
    * [Test Nakama with curl](examples/infra-demo/deploy/07-test-nakama.md)
    * [Test with the Unity client and clean up](examples/infra-demo/deploy/08-test-client-and-cleanup.md)
    * [Reading the manifests in `deploy/k8s/`](examples/infra-demo/deploy/manifest-walkthrough.md)
    * [Traffic path and where TLS is configured](examples/infra-demo/deploy/traffic-and-tls.md)
  * [Unity client: open the project, build the scenes, build the player, run it](examples/infra-demo/unity-client.md)
  * [Operations](examples/infra-demo/operations/README.md)
    * [Status, logs, scaling, restarts and image updates](examples/infra-demo/operations/01-status-and-updates.md)
    * [Safe shutdown (drain) and player accounts](examples/infra-demo/operations/02-drain-and-accounts.md)
    * [TLS and Nakama keys](examples/infra-demo/operations/03-tls-and-keys.md)
    * [Monitoring](examples/infra-demo/operations/04-monitoring.md)
    * [Autoscaling, NetworkPolicy, backups and the public address](examples/infra-demo/operations/05-scaling-security-backup.md)
  * [Architecture](examples/infra-demo/architecture/overview.md)
    * [Backend](examples/infra-demo/architecture/backend.md)
    * [Nakama module](examples/infra-demo/architecture/nakama-module.md)
    * [Game server (pod)](examples/infra-demo/architecture/game-server.md)
    * [Unity client code](examples/infra-demo/architecture/client-code.md)
    * [RPC interface](examples/infra-demo/architecture/rpc-api.md)
    * [Using fRPC](examples/infra-demo/architecture/using-frpc.md)
    * [Add an fRPC method](examples/infra-demo/architecture/frpc-add-a-method.md)
    * [Development guide](examples/infra-demo/architecture/development.md)
  * [Testing](examples/infra-demo/testing.md)
  * [Troubleshooting](examples/infra-demo/troubleshooting.md)
  * [Reference](examples/infra-demo/reference.md)

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
