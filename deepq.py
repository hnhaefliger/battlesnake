import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from battlesnake import *

# Configuration parameters for the whole setup
seed = 42
gamma = 0.99  # Discount factor for past rewards
max_steps_per_episode = 10000
# Smallest number such that 1.0 + eps != 1.0
eps = np.finfo(np.float32).eps.item()

num_actions = 4
num_hidden = 256

inputs = layers.Input(shape=(5, 11, 11))
inner = layers.Flatten()(inputs)
common = layers.Dense(num_hidden, activation="relu")(inner)
action = layers.Dense(num_actions, activation="softmax")(common)
critic = layers.Dense(1)(common)

model = keras.Model(inputs=inputs, outputs=[action, critic])

optimizer = keras.optimizers.Adam(learning_rate=0.01)
huber_loss = keras.losses.Huber()
action_probs_history = []
critic_value_history = []
rewards_history = []
running_reward = 0
episode_count = 0

while True:  # Run until solved
    raw_state = create_random_state(11, 11)

    episode_reward = 0
    with tf.GradientTape() as tape:
        for timestep in range(1, max_steps_per_episode):
            state = tf.convert_to_tensor(snake_tensors(raw_state))

            action_probs, critic_value = model(state)
            critic_value_history.append(critic_value[0, 0])

            action = [np.random.choice(num_actions, p=np.squeeze(probs)) for probs in action_probs]
            action_probs_history.append([tf.math.log(probs[a]) for probs, a in zip(action_probs, action)])

            # Apply the sampled action in our environment
            raw_state, reward, done, _ = next_state_and_scores(raw_state, [['up', 'down', 'left', 'right'][a] for a in action])
            reward = tf.reduce_mean(reward).numpy()
            state = tf.convert_to_tensor(snake_tensors(raw_state))
            rewards_history.append(reward)
            episode_reward += reward

            if done:
                break

        # Update running reward to check condition for solving
        running_reward = 0.05 * episode_reward + (1 - 0.05) * running_reward

        # Calculate expected value from rewards
        # - At each timestep what was the total reward received after that timestep
        # - Rewards in the past are discounted by multiplying them with gamma
        # - These are the labels for our critic
        returns = []
        discounted_sum = 0
        for r in rewards_history[::-1]:
            discounted_sum = r + gamma * discounted_sum
            returns.insert(0, discounted_sum)

        # Normalize
        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
        returns = returns.tolist()

        # Calculating loss values to update our network
        history = zip(action_probs_history, critic_value_history, returns)
        actor_losses = []
        critic_losses = []
        for log_prob, value, ret in history:
            # At this point in history, the critic estimated that we would get a
            # total reward = `value` in the future. We took an action with log probability
            # of `log_prob` and ended up recieving a total reward = `ret`.
            # The actor must be updated so that it predicts an action that leads to
            # high rewards (compared to critic's estimate) with high probability.
            diff = ret - value
            actor_losses.append([-l * diff for l in log_prob])  # actor loss

            # The critic must be updated so that it predicts a better estimate of
            # the future rewards.
            critic_losses.append(
                huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
            )

        # Backpropagation
        loss_value = tf.reduce_sum(actor_losses) + tf.reduce_sum(critic_losses)
        grads = tape.gradient(loss_value, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

        # Clear the loss and reward history
        action_probs_history.clear()
        critic_value_history.clear()
        rewards_history.clear()

    # Log details
    episode_count += 1
    if episode_count % 10 == 0:
        template = "running reward: {:.2f} at episode {}"
        print(template.format(running_reward, episode_count))

    if running_reward > 195:  # Condition to consider the task solved
        print("Solved at episode {}!".format(episode_count))
        break
